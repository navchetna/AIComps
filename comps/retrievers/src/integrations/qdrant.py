# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


import os
from types import SimpleNamespace

from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from comps import CustomLogger, EmbedDoc, OpeaComponent, OpeaComponentRegistry, ServiceType

from .config import QDRANT_EMBED_DIMENSION, QDRANT_HOST, QDRANT_INDEX_NAME, QDRANT_PORT

logger = CustomLogger("qdrant_retrievers")
logflag = os.getenv("LOGFLAG", False)


@OpeaComponentRegistry.register("OPEA_RETRIEVER_QDRANT")
class OpeaQDrantRetriever(OpeaComponent):
    """A specialized retriever component derived from OpeaComponent for qdrant retriever services."""

    def __init__(self, name: str, description: str, config: dict = None):
        super().__init__(name, ServiceType.RETRIEVER.name.lower(), description, config)

        health_status = self.check_health()
        if not health_status:
            logger.error("OpeaQDrantRetriever health check failed.")

    def _initialize_client(self, collection_name: str) -> tuple:
        """Initializes the qdrant document store and retriever for a specific collection."""
        qdrant_store = QdrantDocumentStore(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            embedding_dim=QDRANT_EMBED_DIMENSION,
            index=collection_name,
            recreate_index=False,
        )

        retriever = QdrantEmbeddingRetriever(document_store=qdrant_store)

        return qdrant_store, retriever

    def check_health(self) -> bool:
        """Checks the health of the retriever service using the default collection.

        Returns:
            bool: True if the service is reachable and healthy, False otherwise.
        """
        if logflag:
            logger.info("[ check health ] start to check health of QDrant")
        try:
            # Use default collection for health check
            db_store, _ = self._initialize_client(QDRANT_INDEX_NAME)
            _ = db_store.client
            logger.info("[ check health ] Successfully connected to QDrant!")
            return True
        except Exception as e:
            logger.info(f"[ check health ] Failed to connect to QDrant: {e}")
            return False

    async def invoke(self, input: EmbedDoc) -> list:
        """Search the QDrant index for the most similar documents to the input query.

        Args:
            input (EmbedDoc): The input query to search for.
        Output:
            list: The retrieved documents.
        """
        if logflag:
            logger.info(f"[ similarity search ] input: {input}")

        collection_name = input.collection_name or QDRANT_INDEX_NAME
        db_store, retriever = self._initialize_client(collection_name)
        search_res = retriever.run(query_embedding=input.embedding)["documents"]

        # format result to align with the standard output in opea_retrievers_microservice.py
        final_res = []
        for res in search_res:
            dict_res = res.meta
            res_obj = SimpleNamespace(**dict_res)
            final_res.append(res_obj)

        if logflag:
            logger.info(f"[ similarity search ] search result: {final_res}")

        return final_res
