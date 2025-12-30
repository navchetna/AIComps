# Groq for LLM service

## Overview
- Purpose: OpenAI-compatible chat completions microservice backed by Groq's LLM API, exposing a FastAPI endpoint at `/v1/chat/completions`.
- Server Entrypoint: See [AIComps/model-serving/groq/main.py](AIComps/model-serving/groq/main.py). It starts the service via the `MicroService` framework.
- Environment: Requires `GROQ_API_KEY` (and optional `GROQ_MODEL`, default `llama-3.1-8b-instant`).

## Setup

### Docker setup
#### Build image
```bash
cd AIComps;
docker buildx build --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -t navchetna/groq:latest -f model-serving/groq/Dockerfile .;
```

#### Run container

```bash
export GROQ_API_KEY=your_api_key
docker run -p 8000:8000 -e GROQ_API_KEY=$GROQ_API_KEY -e http_proxy=$http_proxy -e https_proxy=$https_proxy navchetna/groq:latest
```

### Configuration
- GROQ_API_KEY: Required to authenticate with Groq.
- GROQ_MODEL: Optional model override; defaults to `llama-3.1-8b-instant`.
- Port/Host: The service binds to `0.0.0.0:8000` by default.

### Client Script
You can also run the service directly via the Python script:

```bash
cd AIComps/model-serving/groq

# Create and activate env
uv venv --python=3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# export env vars
export GROQ_API_KEY=your_api_key
export GROQ_MODEL=llama-3.1-8b-instant

# Run the service
python main.py
```

This starts the server on `http://localhost:8000` and exposes `/v1/chat/completions`.


### Test the service:
```bash
curl -N -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What are the benefits of microservices?"
      }
    ],
    "stream": true
  }'
```

To receive a regular JSON response (non-streaming), set `"stream": false` and remove the SSE header:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "What are the benefits of microservices?" }
    ],
    "stream": false
  }'
```
