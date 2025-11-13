import json
import os
from typing import List, Optional, Union

from fastapi import Body, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models

from comps import CustomLogger, DocPath, OpeaComponent, OpeaComponentRegistry, ServiceType
from comps.cores.proto.api_protocol import DataprepRequest
from comps.dataprep.src.utils import (
    encode_filename,
    get_separators,
    parse_html_new,
    save_content_to_local_disk,
)
from tree_parser.treeparser import TreeParser
from tree_parser.node import Node
from tree_parser.table import Table

import requests

logger = CustomLogger("opea_dataprep_qdrant")
logflag = os.getenv("LOGFLAG", False)

# Embedding model
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")

# LLM/Embedding endpoints
TGI_LLM_ENDPOINT = os.getenv("TGI_LLM_ENDPOINT", "http://localhost:8080")
TGI_LLM_ENDPOINT_NO_RAG = os.getenv("TGI_LLM_ENDPOINT_NO_RAG", "http://localhost:8081")
TEI_EMBEDDING_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT", "")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

DEFAULT_COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag-qdrant")
BASE_OUTPUTS_DIR = os.path.join(os.path.expanduser("~"), "pdf-results")

@OpeaComponentRegistry.register("OPEA_DATAPREP_QDRANT")
class OpeaQdrantDataprep(OpeaComponent):
    """Dataprep component for Qdrant ingestion and search services."""

    def __init__(self, name: str, description: str, config: dict = None):
        super().__init__(name, ServiceType.DATAPREP.name.lower(), description, config)
        self.upload_folder = "./uploaded_files/"
        if TEI_EMBEDDING_ENDPOINT:
            if not HF_TOKEN:
                raise HTTPException(
                    status_code=400,
                    detail="You MUST offer the `HF_TOKEN` when using `TEI_EMBEDDING_ENDPOINT`.",
                )
            import requests

            response = requests.get(TEI_EMBEDDING_ENDPOINT + "/info")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail=f"TEI embedding endpoint {TEI_EMBEDDING_ENDPOINT} is not available."
                )
            model_id = response.json()["model_id"]
            self.embedder = HuggingFaceInferenceAPIEmbeddings(
                api_key=HF_TOKEN, model_name=model_id, api_url=TEI_EMBEDDING_ENDPOINT
            )
        else:
            self.embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

        self.client = None

    def create_qdrant_client(self, host, port):
        """Create a Qdrant client instance with the given host and port."""
        from qdrant_client import QdrantClient
        self.client = QdrantClient(host=host, port=port)

    def check_health(self, host, port) -> bool:
        """Checks the health of the Qdrant service."""
        if self.embedder is None:
            logger.error("Qdrant embedder is not initialized.")
            return False

        try:
            client = QdrantClient(host=host, port=port)
            logger.info(client.info())
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """Checks if a collection exists in Qdrant."""
        try:
            self.client.get_collection(collection_name)
            return True
        except Exception:
            return False

    def invoke(self, *args, **kwargs):
        pass

    def get_table_description(self, item: Table):
        server_host_ip = os.getenv("LLM_SERVER_HOST_IP", "localhost")
        server_port = os.getenv("LLM_SERVER_PORT", 8000)
        model_name = os.getenv("LLM_MODEL_ID")
        use_model_param = os.getenv("LLM_USE_MODEL_PARAM", "false").lower() == "true"
        url = f"http://{server_host_ip}:{server_port}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        data = {
            "messages": [
                {
                    "role": "system",
                    "content": """
                        <s>[INST] <<SYS>>\n You are a helpful, respectful, and honest assistant. Your task is to generate a detailed and descriptive summary of the provided table data in Markdown format, based strictly on the table and its heading. <</SYS>> 
                        [INST] Your job is to create a clear, specific, and **factual** textual description. **Do not add any external information** or provide an abstract summary. Only base the description on the data from the table and its heading.
                        
                        1. Link the **columns** with the corresponding **values** in the rows, referencing the exact terms and terminology from the table. 
                        2. For each row, explain how each column's data relates to the corresponding values. Ensure the description is **step-by-step** and follows the structure of the table in a natural order.
                        3. **Do not return the table itself.** Provide only the descriptive summary, written in **paragraphs**.
                        4. The description should be precise, direct, and **avoid interpretation** or generalization. Stay true to the exact data given.
                        
                        Think carefully and make sure to describe every column and its respective values in detail. 
                    """
                },
                {
                    "role": "user",
                    "content": f"{item.heading}\n{item.markdown_content}",
                }
            ],
            "stream": False
        }

        if use_model_param and model_name:
            data["model"] = model_name
        else:
            data["filename"] = ""

        response = requests.post(url, headers=headers, json=data)
        response_data = json.loads(response.text)
        return response_data['choices'][0]['message']['content']

    def is_table_markdown(self, content_str: str) -> bool:
        """Basic check if a content string is a markdown table."""
        return content_str.strip().startswith('|') and '|' in content_str

    def chunk_node_content(self, node_data: dict, text_splitter: RecursiveCharacterTextSplitter) -> List[str]:
        """Chunks the content of a single JSON node."""
        chunks = []
        content_list = node_data.get("content", [])
        
        for item in content_list:
            if isinstance(item, str):
                if self.is_table_markdown(item):
                    mock_node = Node(0, "Mock Table", "/tmp")
                    mock_table = Table(markdown_content=item, heading="", node=mock_node)
                    table_description = self.get_table_description(mock_table)
                    table_chunks = text_splitter.split_text(table_description)
                    chunks.extend(table_chunks)
                else:
                    text_chunks = text_splitter.split_text(item)
                    chunks.extend(text_chunks)
            else:
                logger.warning(f"Unexpected content type: {type(item)}")
        
        return chunks

    def create_chunks(self, node_data: dict, text_splitter: RecursiveCharacterTextSplitter) -> List[str]:
        """Recursively creates chunks from a JSON node and its children."""
        node_chunks = self.chunk_node_content(node_data, text_splitter)
        
        children = node_data.get("children", [])
        for child in children:
            if isinstance(child, dict) and len(child) == 1:
                child_data = list(child.values())[0]
                node_chunks.extend(self.create_chunks(child_data, text_splitter))
            else:
                logger.warning(f"Unexpected child structure: {child}")
        
        return node_chunks

    async def ingest_data_to_qdrant(self, json_tree_path: str, collection_name: str, user: str, filename: str, chunk_size: int = 2000, chunk_overlap: int = 200, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        """Ingest document to Qdrant using JSON tree parsing logic."""
        if not qdrant_host or not qdrant_port:
            raise HTTPException(status_code=400, detail="qdrant_host and qdrant_port must be provided")

        if logflag:
            logger.info(f"Parsing JSON {json_tree_path} for collection {collection_name}.")

        if not os.path.exists(json_tree_path):
            raise HTTPException(status_code=404, detail=f"JSON file not found: {json_tree_path}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
            separators=get_separators(),
        )

        with open(json_tree_path, 'r') as f:
            tree_data = json.load(f)
        root_data = tree_data['root']

        chunks = self.create_chunks(root_data, text_splitter)

        if logflag:
            logger.info(f"Done preprocessing. Created {len(chunks)} chunks from the JSON file.")

        self.create_qdrant_client(qdrant_host, qdrant_port)
        if not self.check_health(qdrant_host, qdrant_port):
            raise HTTPException(status_code=503, detail="Qdrant service is not healthy.")

        if not self.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )

        batch_size = 32
        num_chunks = len(chunks)
        for i in range(0, num_chunks, batch_size):
            batch_chunks = chunks[i : i + batch_size]
            metadatas = [{"user": user, "filename": filename} for _ in batch_chunks]
            batch_texts = batch_chunks

            _ = Qdrant.from_texts(
                texts=batch_texts,
                embedding=self.embedder,
                metadatas=metadatas,
                collection_name=collection_name,
                host=qdrant_host,
                port=qdrant_port,
            )
            if logflag:
                logger.info(f"Processed batch {i//batch_size + 1}/{(num_chunks-1)//batch_size + 1} for collection {collection_name}")

        return True
    
    def extract_folder_name_from_file_path(self, file_path: str) -> str:
        """
        Extracts the folder name from a file path.
        For example: 
        - '/home/user/outputs/AI_Servers_Lenovo/output_tree.json' -> 'AI_Servers_Lenovo'
        - 'output_tree.json' -> None (no folder in path)
        """
        dir_path = os.path.dirname(file_path)
        if dir_path:
            folder_name = os.path.basename(dir_path)
            return folder_name
        return None

    async def ingest_files(
        self,
        input: DataprepRequest,
        collection_name: Optional[str] = DEFAULT_COLLECTION_NAME,
    ):
        """Ingest content from user's outputs folder into Qdrant database.

        Requires 'user' and 'filename' in input. Constructs path to output_tree.json and ingests it.
        Returns '{"status": 200, "message": "Data preparation succeeded"}' if successful.
        Args:
            input (DataprepRequest): Model containing parameters including user (str), filename (str), etc.
            collection_name (Optional[str]): The Qdrant collection to ingest into. Defaults to env var COLLECTION_NAME.
        """
        user = input.user
        filename = input.filename
        chunk_size = input.chunk_size
        chunk_overlap = input.chunk_overlap
        process_table = input.process_table
        table_strategy = input.table_strategy
        qdrant_host = input.qdrant_host
        qdrant_port = input.qdrant_port

        if not user or not filename or not qdrant_host or not qdrant_port:
            raise HTTPException(status_code=400, detail="Must provide user, filename, qdrant_host, and qdrant_port.")

        folder_name = self.extract_folder_name_from_file_path(filename)
        
        if not folder_name:
            folder_name = os.path.splitext(os.path.basename(filename))[0]

        folder_path = os.path.join(BASE_OUTPUTS_DIR, user, 'outputs', folder_name)
        json_tree_path = os.path.join(folder_path, 'output_tree.json')

        print("Folder path: ", folder_path)
        print("JSON tree path: ", json_tree_path)

        if not os.path.exists(json_tree_path):
            raise HTTPException(
                status_code=404,
                detail=f"output_tree.json does not exist at {json_tree_path}. Please parse the PDF to generate a markdown."
            )

        if logflag:
            logger.info(f"Ingesting {json_tree_path} into collection: {collection_name}")

        await self.ingest_data_to_qdrant(
            json_tree_path=json_tree_path,
            collection_name=collection_name,
            user=user,
            filename=folder_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port
        )

        result = {"status": 200, "message": "Data preparation succeeded"}
        if logflag:
            logger.info(result)
        return result

    async def get_files(self, collection_name: Optional[str] = DEFAULT_COLLECTION_NAME, qdrant_host: str = None, qdrant_port: int = None):
        """Get file structure from Qdrant collection in the format of
        {
            "name": "File Name",
            "id": "File Name",
            "type": "File",
            "parent": "",
        }"""
        if not qdrant_host or not qdrant_port:
            raise HTTPException(status_code=400, detail="qdrant_host and qdrant_port must be provided")

        self.create_qdrant_client(qdrant_host, qdrant_port)
        if not self.check_health(qdrant_host, qdrant_port):
            raise HTTPException(status_code=503, detail="Qdrant service is not healthy.")

        if not self.collection_exists(collection_name):
            raise HTTPException(status_code=404, detail=f"Collection {collection_name} does not exist.")

        result = self.client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True,
        )
        files = set()
        file_structure = []
        for point in result[0]:
            if 'metadata' in point.payload and 'file_path' in point.payload['metadata']:
                file_path = point.payload['metadata']['file_path']
                if file_path not in files:
                    files.add(file_path)
                    file_structure.append({
                        "name": os.path.basename(file_path),
                        "id": file_path,
                        "type": "File",
                        "parent": "",
                    })

        if logflag:
            logger.info(f"Retrieved files from collection {collection_name}: {file_structure}")
        return file_structure

    async def delete_files(self, file_path: str, collection_name: Optional[str] = DEFAULT_COLLECTION_NAME, qdrant_host: str = None, qdrant_port: int = None):
        """Delete file according to `file_path` from the specified collection.

        `file_path`:
            - specific file path (e.g. /path/to/file.txt): delete points related to this file
            - "all": delete all points in the collection
        """
        if not qdrant_host or not qdrant_port:
            raise HTTPException(status_code=400, detail="qdrant_host and qdrant_port must be provided")

        self.create_qdrant_client(qdrant_host, qdrant_port)
        if not self.check_health(qdrant_host, qdrant_port):
            raise HTTPException(status_code=503, detail="Qdrant service is not healthy.")

        if not self.collection_exists(collection_name):
            raise HTTPException(status_code=404, detail=f"Collection {collection_name} does not exist.")

        if file_path == "all":
            self.client.delete_collection(collection_name)
            if logflag:
                logger.info(f"Deleted all files from collection {collection_name}")
            return {"status": 200, "message": f"All files deleted from collection {collection_name}"}
        else:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="metadata.file_path",
                                match=models.MatchValue(value=file_path),
                            )
                        ]
                    )
                ),
            )
            if logflag:
                logger.info(f"Deleted file {file_path} from collection {collection_name}")
            return {"status": 200, "message": f"File {file_path} deleted from collection {collection_name}"}

    async def get_list_of_collections(self, qdrant_host: str = None, qdrant_port: int = None):
        """Get list of all collections in Qdrant."""
        if not qdrant_host or not qdrant_port:
            raise HTTPException(status_code=400, detail="qdrant_host and qdrant_port must be provided")

        self.create_qdrant_client(qdrant_host, qdrant_port)
        if not self.check_health(qdrant_host, qdrant_port):
            raise HTTPException(status_code=503, detail="Qdrant service is not healthy.")

        collections = self.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        if logflag:
            logger.info(f"List of collections: {collection_names}")
        return collection_names
