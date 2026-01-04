# Retriever Microservice with Qdrant

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Deployment Setup with Docker](#deployment-setup-with-docker)
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

```bash
export no_proxy=${your_no_proxy}
export http_proxy=${your_http_proxy}
export https_proxy=${your_https_proxy}

export EMBED_DIMENSION=${your_embedding_dimension}  # e.g., (Optional - Default: 768)
export INDEX_NAME=${your_index_name}                 # e.g., (Optional - Default: rag-qdrant)

# Optional: TEI Embedding endpoint (if using Text Embeddings Inference)
export TEI_EMBEDDING_ENDPOINT="http://${your_ip}:6060"

# Retriever service port (optional, defaults to 7000)
export RETRIEVER_PORT=7000
```

---

## Development Setup

For local development without Docker, follow these steps:

### Prerequisites

1. **Install `uv`**
2. **Create a virtual environment with uv**
3. **Install the AIComps package** from the root directory. See: [Install AIComps](../../../../README.md#installation)

### Install Dependencies

Install the retriever-specific dependencies:
```bash
cd AIComps/tasks/text/retrievers
uv pip install -r src/requirements-cpu.txt
```

### Setup Environment Variables

Before running the service, configure the required environment variables:

```bash
export no_proxy=${your_no_proxy}
export http_proxy=${your_http_proxy}
export https_proxy=${your_https_proxy}

export EMBED_DIMENSION=768
export INDEX_NAME=rag-qdrant

# Optional: TEI Embedding endpoint
export TEI_EMBEDDING_ENDPOINT="http://localhost:6060"

# Retriever service port (optional, defaults to 7000)
export RETRIEVER_PORT=7000
```

### Run the Microservice

Navigate to the `src` directory and run the OPEA microservice:
```bash
cd src
python opea_retrievers_microservice.py
```

The service will start on port 7000 by default.

#### Configure Custom Port

You can configure a custom port in two ways:

**Option 1: Using environment variable**
```bash
export RETRIEVER_PORT=8080
python opea_retrievers_microservice.py
```

**Option 2: Using CLI argument** (overrides environment variable)
```bash
python opea_retrievers_microservice.py --port 8080
```

---

## Deployment Setup with Docker

### Build Docker Image

```bash
cd ../../../../ # to the project root dir (AIComps)
```
```bash
docker build -t navchetna/retriever:latest --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f tasks/text/retrievers/src/Dockerfile .
```

### Run Docker with CLI

```bash
docker run -d --name="retriever-qdrant-server" -p 7000:7000 --ipc=host -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy -e RETRIEVER_COMPONENT_NAME="OPEA_RETRIEVER_QDRANT" -e TEI_EMBEDDING_ENDPOINT=$TEI_EMBEDDING_ENDPOINT navchetna/retriever:latest
```

#### Configure Custom Port for Docker

To run the service on a custom port (default is 7000):
```bash
docker run -d --name="retriever-qdrant-server" -p 8080:8080 --ipc=host -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy -e RETRIEVER_COMPONENT_NAME="OPEA_RETRIEVER_QDRANT" -e TEI_EMBEDDING_ENDPOINT=$TEI_EMBEDDING_ENDPOINT -e RETRIEVER_PORT=8080 navchetna/retriever:latest
```

<!-- ### Run Docker with Docker Compose

```bash
cd tasks/text/retrievers/deployment/docker_compose
export service_name="retriever-qdrant"
docker compose -f compose.yaml up ${service_name} -d
``` -->

---

## Invoke Microservice

Once the retriever microservice for Qdrant is started, you can use the following commands to invoke the microservice for document retrieval.

### Check Service Status

Verify the service is running:
```bash
curl -X GET http://localhost:7000/v1/health_check \
  -H 'Content-Type: application/json'
```

### Retrieve Documents

To consume the Retriever Microservice, you can generate a mock embedding vector of length **768** with Python.
> *If running a containerized service, then you will need to define the **hostname/IP** in the curl command for the Qdrant server*

**Basic retrieval with text and embedding:**
```bash
# May need to activate env
export your_embedding=$(python -c "import random; embedding = [random.uniform(-1, 1) for _ in range(768)]; print(embedding)")

curl -X POST http://localhost:7000/v1/retrieval \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Can LLMs generate ideas?",
    "embedding": '"${your_embedding}"',
    "qdrant_host": "localhost",
    "qdrant_port": 6333
  }' | jq
```

**Retrieve from a specific Qdrant collection:**

By default, the service uses the collection name from the `INDEX_NAME` environment variable (e.g., `rag-qdrant`). To retrieve from a different collection:

```bash
export your_embedding=$(python -c "import random; embedding = [random.uniform(-1, 1) for _ in range(768)]; print(embedding)")

curl -X POST http://localhost:7000/v1/retrieval \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Can LLMs generate ideas?",
    "embedding": '"${your_embedding}"',
    "collection_name": "your-custom-collection",
    "qdrant_host": "localhost",
    "qdrant_port": 6333
  }' | jq
```

**Additional retrieval parameters:**

You can customize the retrieval behavior with additional parameters:

```bash
export your_embedding=$(python -c "import random; embedding = [random.uniform(-1, 1) for _ in range(768)]; print(embedding)")

curl -X POST http://localhost:7000/v1/retrieval \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Can LLMs generate ideas?",
    "embedding": '"${your_embedding}"',
    "collection_name": "your-collection",
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
    "search_type": "similarity",
    "k": 10
  }' | jq
```

> **Note:** The `embedding` parameter is optional if you have configured a `TEI_EMBEDDING_ENDPOINT`. In that case, the service will automatically generate embeddings from the input text.