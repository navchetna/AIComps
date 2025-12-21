# Dataprep Microservice with Qdrant

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup (uv)](#environment-setup-uv)
3. [Start Qdrant](#start-qdrant)
4. [Run Microservice](#run-microservice)
5. [Invoke Microservice](#invoke-microservice)
6. [Running in the air gapped environment](#running-in-the-air-gapped-environment)

## Prerequisites

- Ensure a Qdrant server is running and reachable (default dashboard: http://localhost:6333/dashboard).
- Ensure an LLM service is available if using table description.
    See: [How to spin up a Groq service](../../groq/README.md)

## Environment Setup (uv)

Install dependencies and create a virtual environment using `uv`.

```bash
# Install uv (Linux/macOS)
curl -Ls https://astral.sh/uv/install.sh | sh

# Navigate to the dataprep microservice directory
cd AIComps/tasks/text/dataprep/src

# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate

# Install Python dependencies
uv pip install -r requirements.txt
```

### Setup Environment Variables
```bash
export no_proxy=${your_no_proxy}
export http_proxy=${your_http_proxy}
export https_proxy=${your_https_proxy}
export COLLECTION_NAME=rag-qdrant
export PYTHONPATH=/path/to/AIComps

# LLM service configuration
export LLM_SERVER_HOST_IP=localhost
export LLM_SERVER_PORT=8000
export LLM_MODEL_ID=llama-3.1-8b-instant
```

### Start Qdrant Server

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```
Once Qdrant is running, you can access the Qdrant Web UI dashboard in your browser at:
```bash
http://localhost:6333/dashboard
```

> Note: If Qdrant is not on localhost, adjust `qdrant_host` and `qdrant_port` accordingly when invoking the microservice.

## Run Microservice

Start the dataprep microservice from the activated environment.

```bash
cd AIComps/tasks/text/dataprep/src
python opea_dataprep_microservice.py
```

## Invoke Microservice

Once document preparation microservice for Qdrant is started, user can use below command to invoke the microservice to convert the document to embedding and save to the database.

> Only supports JSON tree structure for now

```bash
curl -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "filename=NAME_OF_THE_FILE" \
    -F "qdrant_host=QDRANT_HOST" \
    -F "qdrant_port=QDRANT_PORT" \
    -F "user=YOUR_USERNAME" \
    http://localhost:5000/v1/dataprep/ingest
```

Send request to a specific collection: (defaults to rag-qdrant)
```bash
curl -X POST \
    -F "filename=NAME_OF_THE_FILE" \
    -F "qdrant_host=QDRANT_HOST" \
    -F "qdrant_port=QDRANT_PORT" \
    -F "user=YOUR_USERNAME" \
    -F "collection_name=your_collection" \
    http://localhost:5000/v1/dataprep/ingest
```

You can specify chunk_size and chunk_overlap by the following commands.

```bash
curl -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "filename=NAME_OF_THE_FILE" \
    -F "qdrant_host=QDRANT_HOST" \
    -F "qdrant_port=QDRANT_PORT" \
    -F "user=YOUR_USERNAME" \
    -F "chunk_size=2000" \
    -F "chunk_overlap=200" \
    http://localhost:5000/v1/dataprep/ingest
```

We support table extraction from pdf documents. You can specify process_table and table_strategy by the following commands. "table_strategy" refers to the strategies to understand tables for table retrieval. As the setting progresses from "fast" to "hq" to "llm," the focus shifts towards deeper table understanding at the expense of processing speed. The default strategy is "fast".

Note: If you specify "table_strategy=llm", You should first start TGI Service, please refer to 1.2.1, 1.3.1 in https://github.com/opea-project/GenAIComps/tree/main/comps/llms/README.md, and then `export TGI_LLM_ENDPOINT="http://${your_ip}:8008"`.

```bash
curl -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "filename=NAME_OF_THE_FILE" \
    -F "qdrant_host=QDRANT_HOST" \
    -F "qdrant_port=QDRANT_PORT" \
    -F "user=YOUR_USERNAME" \
    -F "process_table=true" \
    -F "table_strategy=hq" \
    http://localhost:5000/v1/dataprep/ingest
```

## Running in the air gapped environment

Please follow the [common guide](../README.md#running-in-the-air-gapped-environment) to run dataprep microservice in the air gapped environment.

