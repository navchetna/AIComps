# Summarization Service

> A FastAPI-based service that transforms long text into concise, intelligent summaries using OpenAI-compatible LLMs with **Groq** fallback support.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

- **Smart Summarization** - Generate concise summaries from any text input
- **Custom Prompts** - Control tone, style, and emphasis with configurable prompts  
- **Flexible Word Limits** - Set custom word limits per request
- **Dual Backend Support** - OpenAI-compatible API with automatic Groq fallback
- **Modular Design** - Use as standalone service or Python module

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip for package management

### Setup Virtual Environment

We recommend using `uv` for fast and reliable package management:

**Option 1: Using uv (Recommended)**
```bash
# Create virtual environment
uv venv --python 3.10

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

**Option 2: Using traditional pip**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in your project root:

```bash
# Comment out the service you do not want to use!
# 1. OpenAI-compatible hosted model
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# 2. Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

> **Note:** `prompt` and `word_limit` are configured per request, not in environment variables.

### Launch the Service

**Option 1: Direct execution**
```bash
python main.py
```

**Option 2: Using uvicorn with auto-reload (Development)**
```bash
uvicorn main:app --reload
```
 **Service will be available at:** `http://127.0.0.1:8000`

---

# Docker Deployment

## Building as a Component
For production deployments or component-based architectures, you can containerize the service:


Build with proxy support (if needed)
```bash
cd summarization/src
docker buildx build --build-arg HTTP_PROXY=$HTTP_PROXY --build-arg HTTPS_PROXY=$HTTPS_PROXY --build-arg https_proxy=$HTTPS_PROXY --build-arg http_proxy=$HTTP_PROXY -t summarization-service -f /path/to/your/Dockerfile .
```
Run the Container
```bash
docker run -d --name summarization-service -p 8000:8000 -e OPENAI_API_KEY=your_openai_api_key -e OPENAI_API_BASE=http://your.model.endpoint.com/v1 -e GROQ_API_KEY=your_groq_api_key -e HTTP_PROXY=$HTTP_PROXY -e HTTPS_PROXY=$HTTPS_PROXY -e https_proxy=$HTTPS_PROXY -e http_proxy=$HTTP_PROXY summarization-service
```
Container Management
```bash
# View logs
docker logs summarization-service

# Stop the service
docker stop summarization-service

# Remove the container
docker rm summarization-service

# Check container status
docker ps -a | grep summarization-service
```
---

## API Reference

### `POST /summarize`

Transform your text into summaries with customizable parameters.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | ✅ **Yes** | The text you want to summarize |
| `prompt` | `string` | ❌ No | Custom prompt to guide summarization style |
| `word_limit` | `integer` | ❌ No | Maximum words in the summary |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `summary` | `string` | The generated summary |
| `model` | `string` | Model used for generation |
| `backend` | `string` | Backend used (`vLLM` or `groq`) |

---

## Usage Examples

### 1. **Basic Summarization**
*Default prompt and word limit*

```bash
curl -X POST "http://127.0.0.1:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI is a modern, high-performance web framework for building APIs with Python. It is built on top of Starlette and Pydantic. It is designed to be easy to use and fast to run."
  }' | jq
```

### 2. **Custom Word Limit**
*Precise control over summary length*

```bash
curl -X POST "http://127.0.0.1:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI is a modern, high-performance web framework for building APIs with Python. It is built on top of Starlette and Pydantic. It is designed to be easy to use and fast to run.",
    "word_limit": 50
  }' | jq
```

### 3. **Custom Prompt Style**
*Creative and engaging summaries*

```bash
curl -X POST "http://127.0.0.1:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI is a modern, high-performance web framework for building APIs with Python. It is built on top of Starlette and Pydantic. It is designed to be easy to use and fast to run.",
    "prompt": "Summarize this text in a humorous tone",
    "word_limit": 40
  }' | jq
```

### 4. **Long Text Processing**
*Complex content with precise word limits*

```bash
curl -X POST "http://127.0.0.1:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial Intelligence (AI) has rapidly evolved over the past decade, transforming industries, healthcare, education, and transportation. With machine learning, natural language processing, and computer vision advancements, AI systems can analyze massive datasets, predict trends, automate tasks, and provide intelligent insights that drive innovation across sectors.",
    "word_limit": 40
  }' | jq
```


## Error Handling

The service provides detailed error responses:

- **500 Internal Server Error:** When LLM API calls fail
- **422 Validation Error:** For invalid request parameters
- **Detailed Messages:** Clear error descriptions for debugging


## Contributing

We welcome contributions! Feel free to:

- Report bugs
- Suggest features  
- Submit pull requests
- Improve documentation

