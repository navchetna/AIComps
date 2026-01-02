import argparse
import os
import sys
import time
from typing import Union

from fastapi import Body, Depends, HTTPException, Request, UploadFile, File
from integrations.qdrant import OpeaQdrantDataprep
from opea_dataprep_loader import OpeaDataprepLoader

from AIComps.tasks import (
    CustomLogger,
    ServiceType,
    opea_microservices,
    register_microservice,
    register_statistics,
    statistics_dict,
)
from AIComps.tasks.cores.proto.api_protocol import (
    DataprepRequest,
    QdrantDataprepRequest,
)
from AIComps.tasks.text.dataprep.src.utils import create_upload_folder

logger = CustomLogger("opea_dataprep_microservice")
logflag = os.getenv("LOGFLAG", False)
upload_folder = "./uploaded_files/"

# Parse CLI arguments early to determine port before decorators are evaluated
def _get_port():
    """Get port from CLI args or environment variable"""
    default_port = int(os.getenv("DATAPREP_PORT", 5000))
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="OPEA Dataprep Microservice", add_help=False)
        parser.add_argument("--port", type=int, default=default_port)
        args, _ = parser.parse_known_args()
        return args.port
    return default_port

DATAPREP_PORT = _get_port()

dataprep_component_name = os.getenv("DATAPREP_COMPONENT_NAME", "OPEA_DATAPREP_QDRANT")
# Initialize OpeaComponentLoader
loader = OpeaDataprepLoader(
    dataprep_component_name,
    description=f"OPEA DATAPREP Component: {dataprep_component_name}",
)

async def resolve_dataprep_request(request: Request):
    form = await request.form()
    
    user = form.get("user")
    if not user:
        raise HTTPException(status_code=400, detail="Missing required 'user' field.")

    filename = form.get("filename")
    if not filename:
        files = form.getlist("files")
        if files and len(files) > 0:
            # Extract filename from the first uploaded file
            uploaded_file = files[0]
            if hasattr(uploaded_file, 'filename'):
                filename = uploaded_file.filename
            else:
                filename = str(uploaded_file)
        
        if not filename:
            raise HTTPException(status_code=400, detail="Missing required 'filename' field or uploaded file.")

    qdrant_host = form.get("qdrant_host")
    if not qdrant_host:
        raise HTTPException(status_code=400, detail="Missing required 'qdrant_host' field.")

    qdrant_port = form.get("qdrant_port")
    if not qdrant_port:
        raise HTTPException(status_code=400, detail="Missing required 'qdrant_port' field.")
    else:
        try:
            qdrant_port = int(qdrant_port)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'qdrant_port'. Must be an integer.")

    common_args = {
        "user": user,
        "filename": filename,
        "qdrant_host": qdrant_host,
        "qdrant_port": qdrant_port,
        "files": form.getlist("files") if "files" in form else None,
        "link_list": form.get("link_list", None),
        "chunk_size": int(form.get("chunk_size", 2000)),
        "chunk_overlap": int(form.get("chunk_overlap", 200)),
        "process_table": form.get("process_table", "false").lower() == "true",
        "table_strategy": form.get("table_strategy", "fast"),
    }
    
    if "collection_name" in form:
        print("QdrantDataprepRequest collection name:", form.get("collection_name"))
        return QdrantDataprepRequest(**common_args, collection_name=form.get("collection_name", "rag-qdrant"))

    return QdrantDataprepRequest(**common_args, collection_name="rag-qdrant")

@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/ingest",
    host="0.0.0.0",
    port=DATAPREP_PORT,
)
@register_statistics(names=["opea_service@dataprep"])
async def ingest_files(
    input: Union[DataprepRequest, QdrantDataprepRequest] = Depends(
        resolve_dataprep_request
    ),
):
    if isinstance(input, QdrantDataprepRequest):
        logger.info(f"[ ingest ] Qdrant mode: collection_name={input.collection_name}")
    else:
        logger.info("[ ingest ] Base mode")

    start = time.time()

    files = input.files
    link_list = input.link_list
    
    print("Input parameters")
    print("user:", input.user)
    print("filename:", input.filename)
    if hasattr(input, 'qdrant_host'):
        print("qdrant_host:", input.qdrant_host)
    if hasattr(input, 'qdrant_port'):
        print("qdrant_port:", input.qdrant_port)

    if logflag:
        logger.info(f"[ ingest ] files:{files}")
        logger.info(f"[ ingest ] link_list:{link_list}")

    try:
        response = await loader.ingest_files(input)

        if logflag:
            logger.info(f"[ ingest ] Output generated: {response}")
        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)
        return response
    except Exception as e:
        logger.error(f"Error during dataprep ingest invocation: {e}")
        raise

@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/get",
    host="0.0.0.0",
    port=DATAPREP_PORT,
)
@register_statistics(names=["opea_service@dataprep"])
async def get_files(
    collection_name: str = Body(None, embed=True),
    qdrant_host: str = Body(None, embed=True),
    qdrant_port: int = Body(None, embed=True),
):
    start = time.time()

    if logflag:
        logger.info("[ get ] start to get ingested files")

    try:
        # Use the loader to invoke the component
        if dataprep_component_name == "OPEA_DATAPREP_QDRANT":
            if not qdrant_host or not qdrant_port:
                raise HTTPException(status_code=400, detail="Missing required 'qdrant_host' and 'qdrant_port' for QDRANT.")
            response = await loader.get_files(collection_name, qdrant_host, qdrant_port)
        elif dataprep_component_name == "OPEA_DATAPREP_REDIS":
            response = await loader.get_files(collection_name)
        else:
            if collection_name:
                logger.error(
                    'Error during dataprep get files: "index_name" option is supported if "DATAPREP_COMPONENT_NAME" environment variable is set to "OPEA_DATAPREP_REDIS". i.e: export DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_REDIS"'
                )
                raise
            response = await loader.get_files()

        # Log the result if logging is enabled
        if logflag:
            logger.info(f"[ get ] ingested files: {response}")
        # Record statistics
        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)
        return response
    except Exception as e:
        logger.error(f"Error during dataprep get invocation: {e}")
        raise

@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/delete",
    host="0.0.0.0",
    port=DATAPREP_PORT,
)
@register_statistics(names=["opea_service@dataprep"])
async def delete_files(
    file_path: str = Body(..., embed=True),
    collection_name: str = Body(None, embed=True),
    qdrant_host: str = Body(None, embed=True),
    qdrant_port: int = Body(None, embed=True),
):
    start = time.time()

    if logflag:
        logger.info("[ delete ] start to delete ingested files")

    try:
        # Use the loader to invoke the component
        if dataprep_component_name == "OPEA_DATAPREP_QDRANT":
            if not qdrant_host or not qdrant_port:
                raise HTTPException(status_code=400, detail="Missing required 'qdrant_host' and 'qdrant_port' for QDRANT.")
            response = await loader.delete_files(file_path, collection_name, qdrant_host, qdrant_port)
        elif dataprep_component_name == "OPEA_DATAPREP_REDIS":
            response = await loader.delete_files(file_path, collection_name)
        else:
            if collection_name:
                logger.error(
                    'Error during dataprep delete files: "index_name" option is supported if "DATAPREP_COMPONENT_NAME" environment variable is set to "OPEA_DATAPREP_REDIS". i.e: export DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_REDIS"'
                )
                raise
            response = await loader.delete_files(file_path)

        # Log the result if logging is enabled
        if logflag:
            logger.info(f"[ delete ] deleted result: {response}")
        # Record statistics
        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)
        return response
    except Exception as e:
        logger.error(f"Error during dataprep delete invocation: {e}")
        raise

@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/collections",
    host="0.0.0.0",
    port=DATAPREP_PORT,
)
@register_statistics(names=["opea_service@dataprep"])
async def get_list_of_collections(
    qdrant_host: str = Body(..., embed=True),
    qdrant_port: int = Body(..., embed=True),
):
    start = time.time()
    if logflag:
        logger.info("[ get ] start to get list of collections.")

    if dataprep_component_name != "OPEA_DATAPREP_QDRANT":
        logger.error("Error: Collections are supported only for QDRANT backend.")
        raise HTTPException(status_code=400, detail="Qdrant backend required.")

    try:
        response = await loader.get_list_of_collections(qdrant_host, qdrant_port)

        if logflag:
            logger.info(f"[ get ] list of collections: {response}")

        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)
        return response
    except Exception as e:
        logger.error(f"Error during dataprep get list of collections: {e}")
        raise

@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/indices",
    host="0.0.0.0",
    port=DATAPREP_PORT,
)
@register_statistics(names=["opea_service@dataprep"])
async def get_list_of_indices():
    start = time.time()
    if logflag:
        logger.info("[ get ] start to get list of indices.")

    if dataprep_component_name != "OPEA_DATAPREP_REDIS":
        logger.error(
            'Error during dataprep - get list of indices: "index_name" option is supported if "DATAPREP_COMPONENT_NAME" environment variable is set to "OPEA_DATAPREP_REDIS". i.e: export DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_REDIS"'
        )
        raise

    try:
        response = await loader.get_list_of_indices()

        if logflag:
            logger.info(f"[ get ] list of indices: {response}")

        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)

        return response
    except Exception as e:
        logger.error(f"Error during dataprep get list of indices: {e}")
        raise

if __name__ == "__main__":
    logger.info(f"OPEA Dataprep Microservice is starting on port {DATAPREP_PORT}...")
    create_upload_folder(upload_folder)
    opea_microservices["opea_service@dataprep"].start()
