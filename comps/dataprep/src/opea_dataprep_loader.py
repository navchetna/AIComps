# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


import os

from comps import CustomLogger, OpeaComponentLoader

logger = CustomLogger("opea_dataprep_loader")
logflag = os.getenv("LOGFLAG", False)


class OpeaDataprepLoader(OpeaComponentLoader):
    def __init__(self, component_name, **kwargs):
        super().__init__(component_name=component_name, **kwargs)

    def invoke(self, *args, **kwargs):
        pass

    async def ingest_files(self, input, *args, **kwargs):
        if logflag:
            logger.info("[ dataprep loader ] ingest files")
        if self.component.name == "OPEA_DATAPREP_QDRANT" and hasattr(input, 'collection_name'):
            return await self.component.ingest_files(input, collection_name=input.collection_name)
        return await self.component.ingest_files(input)

    async def get_files(self, *args, **kwargs):
        if logflag:
            logger.info("[ dataprep loader ] get files")
        return await self.component.get_files(*args, **kwargs)

    async def delete_files(self, *args, **kwargs):
        if logflag:
            logger.info("[ dataprep loader ] delete files")
        return await self.component.delete_files(*args, **kwargs)

    async def get_list_of_indices(self, *args, **kwargs):
        if logflag:
            logger.info("[ dataprep loader ] get indices")
        return self.component.get_list_of_indices(*args, **kwargs)
    
    async def get_list_of_collections(self, qdrant_host, qdrant_port):
        if logflag:
            logger.info("[ dataprep loader ] get collections")
        return await self.component.get_list_of_collections(qdrant_host, qdrant_port)
