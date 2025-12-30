# Model Serving

This layer provides model/LLM inference services exposed over HTTP. Each service folder is designed to be containerized and run independently.

## Contents

| Service | Description | Usage |
| --- | --- | --- |
| Groq | Lightweight HTTP service for Groq-backed chat/completions | [README](groq/README.md) |
| vLLM | Notes and setup for serving models via vLLM | [README](vLLM/README.md) |
| Ollama | Notes and setup for local model execution via Ollama | [README](ollama/README.md) |

## Quick start

Pick a service above and follow its README for run/config details.
