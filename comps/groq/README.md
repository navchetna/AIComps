# Groq for LLM service


## Setup

### Build image
```bash
cd AIComps;
docker buildx build --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -t navchetna/groq:latest -f comps/groq/Dockerfile  .;
```

### Run container

```bash
export GROQ_API_KEY=your_api_key
docker run -p 8000:8000 -e GROQ_API_KEY=$GROQ_API_KEY -e http_proxy=$http_proxy -e https_proxy=$https_proxy navchetna/groq:latest
```

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
