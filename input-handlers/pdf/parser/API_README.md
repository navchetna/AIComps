# PDF Parser FastAPI Server

A production-ready FastAPI server for parsing PDFs using the Navchetna Marker PDF Parser, optimized for Intel Xeon processors.

## Features

- 🚀 RESTful API for PDF parsing
- 🤖 Optional LLM enhancement (via vLLM/OpenAI compatible endpoints)
- 📝 Multiple output formats: JSON, Markdown, HTML, Chunks
- 🔧 Configurable OCR and image extraction
- 🐳 Docker and Docker Compose support
- ⚡ Optimized for Intel Xeon CPUs with TCMalloc and IPEX

## Quick Start

### Using Docker Compose (Recommended)

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your configuration:**
   ```bash
   nano .env
   ```

3. **Start the server:**
   ```bash
   docker-compose up -d
   ```

4. **Check server status:**
   ```bash
   curl http://localhost:8000/
   ```

### Manual Setup

1. **Install dependencies** (see main README.md for detailed steps)

2. **Run the server:**
   ```bash
   python server.py
   ```

## API Endpoints

### `GET /`
Root endpoint with server status and configuration information.

**Response:**
```json
{
  "status": "healthy",
  "service": "PDF Parser API",
  "configuration": {
    "use_llm": false,
    "vllm_url": null,
    "force_ocr": false,
    "extract_images": false,
    "output_dir": "/app/outputs"
  }
}
```

### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

### `POST /parse`
Parse a PDF file. Automatically generates both JSON and text outputs.

**Parameters:**
- `file` (required): PDF file to parse
- `user` (required): Username for organizing outputs

**Example:**
```bash
curl -X POST http://localhost:8000/parse \
  -F "file=@document.pdf" \
  -F "user=john" \
  -o result.json
```

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

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USE_LLM` | Enable LLM-based improvements | `false` | No |
| `VLLM_URL` | vLLM service URL | - | Yes (if USE_LLM=true) |
| `OPENAI_API_KEY` | OpenAI API key | `dummy-key-for-vllm` | No |
| `FORCE_OCR` | Force OCR on all pages | `false` | No |
| `EXTRACT_IMAGE` | Extract images from PDFs | `false` | No |
| `OUTPUT_DIR` | Output directory path | `/app/outputs` | No |
| `HOST` | Server host address | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |

## Configuration Examples

### Basic Usage (No LLM, No OCR)
```bash
USE_LLM=false
FORCE_OCR=false
EXTRACT_IMAGE=false
```

### High Accuracy Mode with LLM
```bash
USE_LLM=true
VLLM_URL=http://your-vllm-server:8001/v1
FORCE_OCR=true
EXTRACT_IMAGE=true
```

### OCR Mode Without LLM
```bash
USE_LLM=false
FORCE_OCR=true
EXTRACT_IMAGE=false
```

## Docker Commands

### Build the image:
```bash
docker build -t pdf-parser-api .
```

### Run the container:
```bash
docker run -d \
  -p 8000:8000 \
  -e USE_LLM=false \
  -e FORCE_OCR=false \
  -v $(pwd)/outputs:/app/outputs \
  pdf-parser-api
```

### View logs:
```bash
docker-compose logs -f pdf-parser
```

### Stop the service:
```bash
docker-compose down
```

### Rebuild and restart:
```bash
docker-compose up -d --build
```

## Testing the API

### Using curl:
```bash
# Download a sample PDF
curl -O https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2024-05/intel-xeon-6-product-brief.pdf

# Parse the PDF
curl -X POST http://localhost:8000/parse \
  -F "file=@intel-xeon-6-product-brief.pdf" \
  -F "user=testuser" \
  -o output.json
```

### Using Python:
```python
import requests

url = "http://localhost:8000/parse"

with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"user": "john"}
    response = requests.post(url, files=files, data=data)
    
result = response.json()
print(f"Output directory: {result['output_directory']}")
print(f"JSON output: {result['json_output_path']}")
print(f"Text output: {result['text_output_path']}")
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger):** http://localhost:8000/docs
- **Alternative API docs (ReDoc):** http://localhost:8000/redoc

## Performance Optimization

The Docker image includes:
- **TCMalloc**: For optimized memory allocation
- **Intel Extension for PyTorch (IPEX)**: Hardware acceleration on Xeon CPUs
- **UV Package Manager**: Fast dependency installation

### Resource Recommendations

For optimal performance:
- **Minimum:** 2 CPUs, 4GB RAM
- **Recommended:** 4+ CPUs, 8GB+ RAM
- **High Volume:** 8+ CPUs, 16GB+ RAM

## Troubleshooting

### Container fails to start
```bash
# Check logs
docker-compose logs pdf-parser

# Verify environment variables
docker-compose config
```

### Out of memory errors
Increase memory limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 16G
```

### Slow parsing
- Enable `FORCE_OCR=true` for better accuracy
- Use `USE_LLM=true` with a fast vLLM endpoint
- Increase CPU allocation

### LLM connection errors
Verify `VLLM_URL` is accessible:
```bash
curl http://your-vllm-server:8001/v1/models
```

## Production Deployment

### Using Docker Compose with external vLLM:
```yaml
version: '3.8'

services:
  vllm:
    image: vllm/vllm-openai:latest
    # vLLM configuration...
  
  pdf-parser:
    depends_on:
      - vllm
    environment:
      - USE_LLM=true
      - VLLM_URL=http://vllm:8000/v1
```

### Behind a reverse proxy (nginx):
```nginx
location /pdf-parser/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## License

See the main repository for license information.

## Support

For issues and questions:
- Check the main [README.md](README.md)
- Review [Marker documentation](https://github.com/VikParuchuri/marker)
- Open an issue on the repository
