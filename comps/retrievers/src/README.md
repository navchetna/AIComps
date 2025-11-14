# Retriever Microservice with Qdrant

### Start Qdrant Server
```bash
docker run -d --name=qdrant-db -p 6333:6333 qdrant/qdrant 
```
**Note:** Once Qdrant is running, you can access the Qdrant Web UI dashboard in your browser at:
```
http://localhost:6333/dashboard
```



## 1. 🚀Start Microservice with Python (Option 1)

### 1.1 Install Requirements

```bash

uv pip install -r requirements.txt
```

### 1.2 Setup Environment Variables

```bash
export EMBED_DIMENSION=${your_embedding_dimension}
export INDEX_NAME=${your_index_name}
```

### 1.3 Start Retriever Service

```bash
export TEI_EMBEDDING_ENDPOINT="http://${your_ip}:6060" # Optional
export RETRIEVER_COMPONENT_NAME="OPEA_RETRIEVER_QDRANT"
python opea_retrievers_microservice.py
```
---

## 2. 🚀Start Microservice with Docker (Option 2)

### 2.1 Setup Environment Variables

```bash
export your_ip=<localhost>
export RETRIEVER_COMPONENT_NAME="OPEA_RETRIEVER_QDRANT"
export TEI_EMBEDDING_ENDPOINT="http://${your_ip}:6060" # Optional
```

### 2.2 Build Docker Image

```bash
cd ../../../ # to the project root dir (AIComps)
```
```bash
docker build -t navchetna/retriever:latest --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f comps/retrievers/src/Dockerfile .
```

### 2.3 Run Docker with CLI

```bash
docker run -d --name="retriever-qdrant-server" -p 7000:7000 --ipc=host -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy  -e TEI_EMBEDDING_ENDPOINT=$TEI_EMBEDDING_ENDPOINT -e RETRIEVER_COMPONENT_NAME=$RETRIEVER_COMPONENT_NAME navchetna/retriever:latest
```

<!-- ### 2.4 Run Docker with Docker Compose (Option B)

```bash
cd ../deployment/docker_compose
export service_name="retriever-qdrant"
docker compose -f compose.yaml up ${service_name} -d
``` -->

## 3. 🚀Consume Retriever Service

### 3.1 Check Service Status

```bash
curl -X GET http://$your_ip:7000/v1/health_check \
  -H 'Content-Type: application/json'
```

### 3.2 Consume Embedding Service

To consume the Retriever Microservice, you can generate a mock embedding vector of length **768** with Python.

```bash
export your_embedding=$(python -c "import random; embedding = [random.uniform(-1, 1) for _ in range(768)]; print(embedding)")

curl http://$your_ip:7000/v1/retrieval \
  -X POST \
  -d '{
    "text":"Can LLMs generate ideas?",
    "embedding": '"${your_embedding}"',
    "qdrant_host": "your-qdrant-host",
    "qdrant_port": your-qdrant-port
  }' \
  -H 'Content-Type: application/json' | jq
```

Retrieve from a **specific Qdrant collection**:
```bash
export your_embedding=$(python -c "import random; embedding = [random.uniform(-1, 1) for _ in range(768)]; print(embedding)")

curl http://$your_ip:7000/v1/retrieval \
  -X POST \
  -d '{
    "text":"Can LLMs generate ideas?",
    "embedding": '"${your_embedding}"',
    "collection_name": "your-collection",
    "qdrant_host": "your-qdrant-host",
    "qdrant_port": your-qdrant-port
  }' \
  -H 'Content-Type: application/json' | jq

```