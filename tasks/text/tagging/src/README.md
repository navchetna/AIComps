# Tagging Service

> An intelligent FastAPI-based API service that automatically generates relevant tags from text content using OpenAI-compatible LLMs with **Groq** fallback support.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

- **Smart Tag Generation** - Extract the most relevant tags from any text content
- **Configurable Tag Count** - Set custom number of tags per request (default: 5)
- **Custom Prompts** - Override default behavior with custom tagging instructions
- **Standardized Format** - Automatic lowercase conversion and hyphen-separated multi-word tags
- **Dual Backend Support** - vLLM/OpenAI-compatible API with automatic Groq fallback
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
cd AIComps/tasks/text/tagging/src/
# Create virtual environment and activate
uv venv
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Environment Setup
> **Note:** You need to ensure that you have an LLM service running.  
- Option 1: [Spin up a Groq service](../../../../model-serving/groq/README.md)
- Option 2: [Spin up a vLLM service](../../../../model-serving/vLLM/README.md)

Create a `.env` file in your project root:

```bash
# Choose EITHER one
# OpenAI-compatible hosted model
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=http://localhost:8000/v1 # hosted vllm service
MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct

# Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

> **Note:** `prompt` and `num_tags` are configured per request, not in environment variables.

## Development & Testing (Python)

The Python scripts are intended for development and testing. You can either:

- Run the service directly via `main.py` for a quick local start
- Use `uvicorn` to run the FastAPI app, which exposes the HTTP endpoint

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

## Deployment (Docker)

For deployment, Docker is the supported option. Use the steps below to containerize and run the service.

### Building as a Component

For production deployments or component-based architectures, you can containerize the service:

#### Build the Docker Image

```bash
cd AIComps/tasks/text/tagging/src

# Build with proxy support (if needed)
docker buildx build \
  --build-arg HTTP_PROXY=$HTTP_PROXY \
  --build-arg HTTPS_PROXY=$HTTPS_PROXY \
  --build-arg https_proxy=$HTTPS_PROXY \
  --build-arg http_proxy=$HTTP_PROXY \
  -t tagging-service \
  -f /path/to/your/Dockerfile .
```

#### Run the Container

```bash
docker run -d \
  --name tagging-service \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e OPENAI_API_BASE=http://your.model.endpoint.com/v1 \
  -e GROQ_API_KEY=your_groq_api_key \
  -e HTTP_PROXY=$HTTP_PROXY \
  -e HTTPS_PROXY=$HTTPS_PROXY \
  -e https_proxy=$HTTPS_PROXY \
  -e http_proxy=$HTTP_PROXY \
  tagging-service
```

#### Container Management

```bash
# View logs
docker logs tagging-service

# Stop the service
docker stop tagging-service

# Remove the container
docker rm tagging-service

# Check container status
docker ps -a | grep tagging-service
```

---

## API Reference

### `POST /tags`

Generate tags from your text content with customizable parameters.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | ✅ **Yes** | The text content you want to tag |
| `prompt` | `string` | ❌ No | Custom prompt to guide the tagging behavior |
| `num_tags` | `integer` | ❌ No | Number of tags to generate (default: 5) |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `tags` | `array[string]` | Generated tags in lowercase, hyphen-separated format |
| `model` | `string` | Model used for tag generation |
| `backend` | `string` | Backend used (`vLLM` or `groq`) |

#### Tag Format Rules

- **Lowercase only:** All tags are converted to lowercase
- **Hyphen-separated:** Multi-word tags use hyphens (e.g., "machine-learning")
- **Concise:** Maximum 3 words per tag
- **Relevant:** Highly contextual and informative

---

##  Usage Examples

### 1. **Basic Tag Generation**
*Default settings with 5 tags*

```bash
curl -X POST "http://127.0.0.1:8000/tags" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial Intelligence is transforming healthcare by enabling predictive diagnostics, personalized treatment plans, and automated medical imaging analysis. Machine learning algorithms can now detect diseases earlier and more accurately than traditional methods."
  }'
```

**Response:**
```json
{
  "tags": ["artificial-intelligence", "healthcare-transformation", "predictive-diagnostics", "machine-learning", "medical-imaging"],
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "backend": "vLLM"
}
```

### 2. **Custom Tag Count**
*Generate specific number of tags*

```bash
curl -X POST "http://127.0.0.1:8000/tags" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Climate change is accelerating due to greenhouse gas emissions from fossil fuels, deforestation, and industrial processes. Renewable energy sources like solar and wind power offer sustainable alternatives.",
    "num_tags": 8
  }'
```

### 3. **Custom Prompt Style**
*Specialized tagging behavior*

```bash
curl -X POST "http://127.0.0.1:8000/tags" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The latest smartphone features a 108MP camera, 5G connectivity, and 12GB RAM with advanced AI photography capabilities.",
    "prompt": "Generate tags focusing on technical specifications and features only",
    "num_tags": 3
  }'
```

---

###  **Customization Features**

- **Flexible Tag Count:** Set any number of tags
- **Custom Prompts:** Override default behavior for specialized use cases
- **Format Consistency:** Automatic standardization across all responses
- **Error Handling:** Comprehensive error responses with detailed information


---

## Use Cases

### **Content Management**
- Blog post categorization
- Document organization
- Content discovery systems

### **E-commerce**
- Product categorization
- Search optimization
- Recommendation systems

### **Social Media**
- Hashtag generation
- Content classification
- Trend analysis

---

##  License

**MIT License** - Free to use, modify, and distribute.

---

##  Contributing

We welcome contributions! Feel free to:

-  Report bugs
-  Suggest features  
-  Submit pull requests
-  Improve documentation
