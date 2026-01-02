# Dataprep Microservice with Qdrant

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Depoyment Setup with Docker](#start-microservice-with-docker)
4. [Invoke Microservice](#invoke-microservice)


## Prerequisites
### Start Qdrant Vector DB Server

```bash
docker run --ulimit nofile=65536:65536 -p 6333:6333 -p 6334:6334 qdrant/qdrant
```
Once Qdrant is running, you can access the Qdrant Web UI dashboard in your browser at:
```bash
http://localhost:6333/dashboard
```
> You may need to do SSH tunneling to expose the required port. See: [Accessing the Application via Remote Server](../../../../input-handlers/pdf/viewer/README.md#accessing-the-application-via-remote-server)
---
### Setup Environment Variables

> **Note:** You need to ensure that you have an LLM service running (for table description).  
> See: [How to spin up a Groq service](../../../../model-serving/groq/README.md)

```bash
export no_proxy=${your_no_proxy}
export http_proxy=${your_http_proxy}
export https_proxy=${your_https_proxy}
export COLLECTION_NAME=rag-qdrant

# LLM service configuration
export LLM_SERVER_HOST_IP=localhost
export LLM_SERVER_PORT=8000
export LLM_MODEL_ID=llama-3.1-8b-instant

# Dataprep service port (optional, defaults to 5000)
export DATAPREP_PORT=5000
```


## Development Setup

For local development without Docker, follow these steps:

### Prerequisites

1. **Install `uv`**
2. **Create a virtual environment with uv**
3. **Install the AIComps package** from the root directory

### Install Dependencies

First, install PyTorch with CPU support:
```bash
uv pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cpu
```

Then, install the dataprep-specific dependencies:
```bash
cd AIComps/tasks/text/dataprep
uv pip install -r src/requirements.txt
```

### Setup Environment Variables

Before running the service, configure the required environment variables:

```bash
export no_proxy=${your_no_proxy}
export http_proxy=${your_http_proxy}
export https_proxy=${your_https_proxy}
export COLLECTION_NAME=rag-qdrant

# LLM service configuration
export LLM_SERVER_HOST_IP=localhost
export LLM_SERVER_PORT=8000
export LLM_MODEL_ID=llama-3.1-8b-instant

# Dataprep service port (optional, defaults to 5000)
export DATAPREP_PORT=5000
```

### Run the Microservice

Navigate to the `src` directory and run the OPEA microservice:
```bash
cd src
python opea_dataprep_microservice.py
```

The service will start on port 5000 by default.

#### Configure Custom Port

You can configure a custom port in two ways:

**Option 1: Using environment variable**
```bash
export DATAPREP_PORT=8080
python opea_dataprep_microservice.py
```

**Option 2: Using CLI argument** (overrides environment variable)
```bash
python opea_dataprep_microservice.py --port 8080
```

---

## 🚀Start Microservice with Docker

### Build Docker Image

```bash
cd ../../../../ # to the project root dir (AIComps)
```
```bash
docker build -t navchetna/dataprep:latest --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f tasks/text/dataprep/src/Dockerfile .
```

### Run Docker with CLI
Note that the service assumes your PDF tree will be stored in the HOME directory under `$HOME/pdf-results`
```bash
docker run -d --name="dataprep-qdrant-server" -v $HOME/pdf-results:/home/user/pdf-results --network=host -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy -e DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_QDRANT" -e LLM_SERVER_HOST_IP=$LLM_SERVER_HOST_IP -e LLM_SERVER_PORT=$LLM_SERVER_PORT -e LLM_MODEL_ID=$LLM_MODEL_ID  navchetna/dataprep:latest
```

#### Configure Custom Port for Docker

To run the service on a custom port (default is 5000):
```bash
docker run -d --name="dataprep-qdrant-server" -v $HOME/pdf-results:/home/user/pdf-results --network=host -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy -e DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_QDRANT" -e LLM_SERVER_HOST_IP=$LLM_SERVER_HOST_IP -e LLM_SERVER_PORT=$LLM_SERVER_PORT -e LLM_MODEL_ID=$LLM_MODEL_ID -e DATAPREP_PORT=8080 navchetna/dataprep:latest
```

<!-- ### Run Docker with Docker Compose

```bash
cd comps/dataprep/deployment/docker_compose
docker compose -f compose_qdrant.yaml up -d
``` -->

## Invoke Microservice

Once document preparation microservice for Qdrant is started, user can use below command to invoke the microservice to convert the document to embedding and save to the database.

> Only supports navchetna's JSON tree structure for now

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

You can specify chunk_size and chunk_size by the following commands.

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
