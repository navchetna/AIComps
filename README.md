# AI Reusable Components

Production‑ready, modular AI components to accelerate document and text processing workflows. This monorepo organizes components by layers (input handling, model serving, tasks/services, reusable comps, and models) and provides containerized, API‑driven building blocks you can assemble into end‑to‑end applications.

## Requirements

- Docker (for containerized runs)
- Python 3.10+

## What's Inside

| Layer | Purpose | Notes | Usage |
| --- | --- | --- | --- |
| [Input Handlers](input-handlers/README.md) | Ingest and prepare inputs (PDFs, web pages) | PDF parsing client + viewer tooling | [README](input-handlers/README.md) |
| [Model Serving](model-serving/README.md) | LLM and model inference services | Serving engines: Groq, vLLM, Ollama | [README](model-serving/README.md) |
| [Tasks/Services](tasks/README.md) | Domain tasks (dataprep, retrievers, summarization, tagging) | Each task has its own Dockerfile/requirements | [README](tasks/README.md) |
| [Reusable Comps](comps/README.md) | Standalone microservices/utilities (e.g., vector store) | K8s manifests and Dockerfiles included | [README](comps/README.md) |

Here's what each of the layers include, with links to the relevant READMEs.

---
## Installation

To use these components as a package in your projects, install AIComps in editable mode:

```bash
cd AIComps/
uv pip install -e .
```

After installation, you can navigate into any of the layers (input-handlers, model-serving, tasks, comps) and follow their respective READMEs for detailed usage instructions and setup.

---
## [Input Handlers](input-handlers/README.md)

| Component | Description | Usage |
| --- | --- | --- |
| PDF Parser | Client utilities to call a PDF parsing backend | [README](input-handlers/pdf/parser/README.md) |
| PDF Viewer | A tool to visualize parsed content with RBAC enforcement | [README](input-handlers/pdf/viewer/README.md) |
| Web Crawler | Crawl web content to feed downstream tasks | - |

---

## [Model Serving](model-serving/README.md)

| Service | Description | Usage |
| --- | --- | --- |
| Groq | Lightweight HTTP service for LLM inference via Groq | [README](model-serving/groq/README.md) |
| vLLM | A **high-throughput** framework designed for LLM inference and serving | [README](model-serving/vLLM/README.md) |
| Ollama | Open-source platform designed to run large language models **locally** | [README](model-serving/ollama/README.md) |

---

## [Tasks / Services](tasks/README.md)

These are microservices for common RAG/text workflows. Each subfolder contains `Dockerfile`, `requirements`, and a runnable entrypoint in `src/`.

### - Text

| Task | Description | Usage |
| --- | --- | --- |
| Dataprep | Prepares/cleans text for downstream RAG | [README](tasks/text/dataprep/src/README.md) |
| Retrievers | Retriever microservice to fetch context from the vector DB | [README](tasks/text/retrievers/src/README.md) |
| Summarization | Summarize long content into concise outputs | [README](tasks/text/summarization/src/README.md) |
| Tagging | Auto tag/label text content | [README](tasks/text/tagging/src/README.md) |


### - Speech

| Task | Description | Usage |
| --- | --- | --- |
| ASR (Audio-Speech-Recognition) | Convert speech to text | [README](tasks/speech/asr/Wav2vec2/README.md) |
| Translation | For Indic translations | [README](tasks/speech/translation/IndicTrans2/README.md) |
| TTS (Text-to-Speech) | Convert text to speech | [README](tasks/speech/text2speech/fastspeech2_HS/README.md) |

### - Images

| Task | Description | Usage |
| --- | --- | --- |
| Scene Description | Use vision models to describe content from images | - |

### - Video

| Task | Description | Usage |
| --- | --- | --- |
| Coming Soon | - | - |

<!-- Additional foundations for services live under [tasks/cores](tasks/cores):

| Subsystem | Path | Purpose |
| --- | --- | --- |
| Orchestration (Mega) | [tasks/cores/mega](tasks/cores/mega) | Service orchestration, configs, CLI, and HTTP helpers |
| Protocol & Data | [tasks/cores/proto](tasks/cores/proto) | Shared API protocol utilities and docarray helpers |
| MCP Client | [tasks/cores/mcp](tasks/cores/mcp) | Model Context Protocol client + tooling | -->
<!-- | Storage Adapters | [tasks/cores/storages](tasks/cores/storages) | Adapters for Redis, MongoDB, ArangoDB, etc. | -->


---

<!-- ## Reusable Components (Comps)

| Component | Description | Usage |
| --- | --- | --- |
| Vector Store API | HTTP API for vector storage operations | [README](comps/vector-store/README.md) |
| Vector Store Cleanup | Cleanup/maintenance jobs (e.g., via CronJob) | [README](comps/vector-store/README.md) |
| K8s Manifests | Namespace, RBAC, API Deployment, CronJob | [README](comps/vector-store/README.md) |
| PDF DataPrep Script | Utility script for PDF‑focused preparation workflows | [Script](comps/pdf-dataprep.py) |

See component‑level docs: [comps/vector-store/README.md](comps/vector-store/README.md). -->
<!-- 
--- -->

## Models

| Area | Purpose | Usage |
| --- | --- | --- |
| Embedding | Efficiently convert textual strings into vectorized embeddings | - | 
| Re‑ranking | Semantically reorder retrieved documents by relevance to a query | - | 

---
