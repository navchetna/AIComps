# Models

This layer provides microservices for embedding and reranking operations, essential components for semantic search and RAG (Retrieval-Augmented Generation) workflows. Each service is designed to be containerized and deployed independently with multiple backend implementation options.

## Contents

| Service | Description | Usage |
| --- | --- | --- |
| Embeddings | Convert text/images into vectorized embeddings for semantic search | [README](embeddings/README.md) |
| Rerankings | Semantically reorder retrieved documents by relevance to a query | [README](rerankings/README.md) |

## Quick Start

Each service supports multiple backend implementations (OVMS, TEI) and includes Docker Compose and Kubernetes deployment configurations. Pick a service from the table above and follow its README for run/config details.
