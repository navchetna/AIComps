# Retriever Microservice with Qdrant (Developer Guide)

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup (uv)](#environment-setup-uv)
3. [Start Qdrant](#start-qdrant)
4. [Run Microservice](#run-microservice)
5. [Invoke Microservice](#invoke-microservice)

## Prerequisites

- Ensure a Qdrant server is running and reachable (default dashboard: http://localhost:6333/dashboard).
- Optional: TEI embedding service if you want embeddings generated server-side.
- Set `PYTHONPATH` to your AIComps repo root to resolve imports.

## Environment Setup (uv)

Install dependencies and create a virtual environment using `uv`.

```bash
# Install uv (Linux/macOS)
curl -Ls https://astral.sh/uv/install.sh | sh

# Navigate to the retrievers microservice directory
cd AIComps/tasks/text/retrievers/src

# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate

# Install Python dependencies
uv pip install -r requirements.txt
```

### Setup Environment Variables
```bash
# (Optional) proxy settings
export no_proxy=${your_no_proxy}
export http_proxy=${your_http_proxy}
export https_proxy=${your_https_proxy}

# Required for resolving package imports
export PYTHONPATH=/path/to/AIComps

# Retriever configuration
export RETRIEVER_COMPONENT_NAME=OPEA_RETRIEVER_QDRANT

# (Optional) TEI embedding endpoint if you want server-side embeddings
env | grep TEI_EMBEDDING_ENDPOINT >/dev/null || export TEI_EMBEDDING_ENDPOINT="http://${your_ip}:6060"

# (Optional) typical embedding dimension when crafting mock embeddings
export EMBED_DIMENSION=768
```

## Start Qdrant Server

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```
Once Qdrant is running, you can access the Qdrant Web UI dashboard in your browser at:
```bash
http://localhost:6333/dashboard
```

> Note: If Qdrant is not on localhost, adjust `qdrant_host` and `qdrant_port` accordingly when invoking the microservice.

## Run Microservice

Start the retriever microservice from the activated environment.

```bash
cd AIComps/tasks/text/retrievers/src
python opea_retrievers_microservice.py
```

## Invoke Microservice

You can generate a mock embedding vector of length **768** with Python, then POST to the retrieval endpoint.

```bash
# Generate a mock embedding
export your_embedding=$(python -c "import random; d=int(getattr(__import__('os'),'environ').get('EMBED_DIMENSION','768')); embedding=[random.uniform(-1,1) for _ in range(d)]; print(embedding)")

# Basic retrieval
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Can LLMs generate ideas?",
    "embedding": '"${your_embedding}"',
    "qdrant_host": "your-qdrant-host",
    "qdrant_port": your-qdrant-port
  }' \
  http://localhost:7000/v1/retrieval | jq
```

Retrieve from a **specific Qdrant collection** (defaults to `rag-qdrant` if not provided):
```bash
export your_embedding=$(python -c "import random; d=int(getattr(__import__('os'),'environ').get('EMBED_DIMENSION','768')); embedding=[random.uniform(-1,1) for _ in range(d)]; print(embedding)")

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Can LLMs generate ideas?",
    "embedding": '"${your_embedding}"',
    "collection_name": "your-collection",
    "qdrant_host": "your-qdrant-host",
    "qdrant_port": your-qdrant-port
  }' \
  http://localhost:7000/v1/retrieval | jq
```

### Health Check
```bash
curl -X GET http://localhost:7000/v1/health_check \
  -H 'Content-Type: application/json'
```