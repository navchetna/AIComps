# 🚀 PDF Parser FastAPI Server

> FastAPI server for parsing PDFs with optional LLM enhancement

## 📋 Setup

### Docker Setup (Recommended)

1. **Configure environment variables:**
   ```bash
   cp .env.example .env
   nano .env  # Edit as needed
   ```

2. **Build the Docker image:**
   ```bash
   docker-compose build
   ```

3. **Start the service:**
   ```bash
   docker-compose up -d
   ```

4. **Verify the service is running:**
   ```bash
   curl http://localhost:8000/health
   ```

### Manual Setup

1. **Install dependencies:**
   ```bash
   # Install UV package manager
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create virtual environment
   uv venv .pdf-venv --python 3.12
   source .pdf-venv/bin/activate
   
   # Install requirements
   uv pip install -r requirements.txt
   uv pip install git+https://github.com/navchetna/marker.git
   uv pip install git+https://github.com/navchetna/surya.git
   uv pip install git+https://github.com/navchetna/tree-parser.git
   uv pip install intel_extension_for_pytorch==2.8.0
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   nano .env  # Edit as needed
   ```

3. **Export environment variables:**
   ```bash
   export $(grep -v '^#' .env | xargs)
   ```

4. **Start the server:**
   ```bash
   python server.py
   ```

## 🎯 API Endpoints

### `GET /` - Service Status
Returns current service configuration and status.

```bash
curl http://localhost:8000/
```

### `GET /health` - Health Check
Simple health check endpoint for monitoring.

```bash
curl http://localhost:8000/health
```

### `POST /parse` - Parse PDF
Parse a PDF file with configurable output format.

```bash
curl -X POST http://localhost:8000/parse \
  -F "file=@document.pdf" \
  -F "user=john" \
  -o result.json
```

**Parameters:**
- `file` (required): PDF file to parse
- `user` (required): Username for organizing outputs

**Response:**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "user": "john",
  "output_directory": "/app/outputs/john/document",
  "pdf_path": "/app/outputs/john/document/document.pdf",
  "json_output_path": "/app/outputs/john/document/output_tree.json",
  "text_output_path": "/app/outputs/john/document/output.txt"
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `USE_LLM` | `false` | No | Enable LLM-based improvements |
| `VLLM_URL` | - | Yes (if USE_LLM=true) | vLLM service URL |
| `FORCE_OCR` | `false` | No | Force OCR on all pages |
| `EXTRACT_IMAGE` | `false` | No | Extract images from PDFs |
| `OUTPUT_DIR` | `/app/outputs` | No | Output directory path |
| `HOST` | `0.0.0.0` | No | Server host address |
| `PORT` | `8000` | No | Server port |

### Configuration Examples

**Basic Mode:**
```env
USE_LLM=false
FORCE_OCR=false
EXTRACT_IMAGE=false
```

**High Accuracy Mode:**
```env
USE_LLM=true
VLLM_URL=http://your-vllm:8001/v1
FORCE_OCR=true
EXTRACT_IMAGE=true
```

## 🐳 Docker Commands

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f pdf-parser

# Stop the service
docker-compose down

# Restart the service
docker-compose restart pdf-parser
```

## 🧪 Testing

### Using curl
```bash
# Download test PDF
curl -o test.pdf https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2024-05/intel-xeon-6-product-brief.pdf

# Parse the PDF
curl -X POST http://localhost:8000/parse \
  -F "file=@test.pdf" \
  -F "user=testuser" \
  -o output.json
```

### Using Python
```python
import requests

with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/parse",
        files={"file": f},
        data={"user": "john"}
    )

result = response.json()
print(f"Output directory: {result['output_directory']}")
print(f"JSON output: {result['json_output_path']}")
print(f"Text output: {result['text_output_path']}")
```

## 📚 API Documentation

Interactive API documentation is available when the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## � API Documentation

Interactive API documentation is available when the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Troubleshooting

### Check service logs
```bash
docker-compose logs -f pdf-parser
```

### Verify configuration
```bash
docker-compose config
```

### Test connectivity
```bash
curl http://localhost:8000/health
```

### Common Issues

**Out of memory**: Increase memory limits in docker-compose.yml
```yaml
deploy:
  resources:
    limits:
      memory: 16G
```

**LLM connection errors**: Verify VLLM_URL is accessible
```bash
curl http://your-vllm:8001/v1/models
```

## 📄 License

See main repository for license information.
