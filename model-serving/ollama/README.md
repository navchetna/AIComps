# Setting Up Ollama

Ollama is a powerful tool that allows you to run open-source Large Language Models (LLMs) locally on your system. This guide will walk you through setting up and using Ollama through its API.

## Installation and Initial Setup

### Installing Ollama

1. Download Ollama from the official GitHub repository:
```bash
   curl -fsSL https://ollama.com/install.sh | sh
```

2. Verify installation:
```bash
   ollama --version
```

### Setting Up Your First Model

1. Pull a model (example using Llama 3.2):
```bash
   ollama pull llama3.2:<model_size>
```

2. Run the model to test it:
```bash
   ollama run llama3.2
```
# Serving Ollama:

## Understanding the Ollama API

When you start Ollama, it automatically runs a server on your local machine that listens on port `11434`. The API has several key features:

- Model management (pulling, listing, and deleting models)
- Text generation (completions and chat interactions)
- Embeddings generation
- Fine-tuning capabilities

### API Basics:
- The Ollama API is accessible via HTTP at `http://localhost:11434`
- All API endpoints are prefixed with `/api`
- No API key is required for local usage

## Using the Ollama API

### Basic Text Generation

Use the `/api/generate` endpoint to generate text completions:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "How are you today?",
  "stream": false
}'
```

The `stream` parameter set to `false` will return a single JSON object instead of streaming the response.

### API Request Structure

The generate endpoint requires POST requests with these components:
- Content-Type header set to `application/json`
- JSON body with at least two required keys:
  - `model`: Name of the model (e.g., `"llama3.2"`)
  - `prompt`: The text prompt for the model

## Programming with the Ollama API

### Python Integration Example
```python
import requests
import json

curl = "http://localhost:11434/api/generate"
headers = {"Content-Type": "application/json"}
data = {
    "model": "llama3.2",
    "prompt": "What is water made of?",
    "stream": False
}

response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()
print(result["response"])
```
### Advanced API Parameters

You can customize model behavior with additional parameters:
```
{
  "model": "llama3.2",
  "prompt": "Write a short poem about coding",
  "system": "You are a helpful assistant that writes poetry",
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "max_tokens": 500
}
```

## API Debugging and Troubleshooting

### Checking API Status

Verify the Ollama service is running:
```bash
curl http://localhost:11434/api/version
```

### Common Issues and Solutions

1. Ensure Ollama is running before making API calls.
2. Verify your model is correctly downloaded using:
   ollama list
3. Check that port `11434` isn't blocked by firewall settings.

## Docker Integration

When using Ollama with Docker, you may need to adjust the API URL:
- Use `http://host.docker.internal:11434` from a Docker container.
- Use your machine's actual IP like `http://192.168.1.100:11434`.
- Use `http://localhost:11434` for local source code deployment.

## Available Models

You can use various models with Ollama. Some popular options include:

- **Llama 3.2** (1B to 90B parameters)
- **DeepSeek-R1**
- **Phi 4**
- **Gemma 2**
- **Mistral**
- And many more specialized models...

Check which models you have installed:
```bash
ollama list
```

This should help you get started with setting up and using the Ollama API for integrating powerful LLMs into your applications locally.
