# AI Reusable Components

A collection of production-ready, modular AI components designed to accelerate the development of intelligent applications. This repository provides a comprehensive suite of pre-built components that handle common AI workflows, from document processing to content generation.

## Overview

This repository contains containerized, API-driven components that can be easily integrated into your AI applications. Each component is designed with scalability, reliability, and ease of use in mind, allowing developers to focus on building innovative solutions rather than implementing foundational AI capabilities from scratch.

## Available Components

### Document Processing
- **PDF Parser** - Extract text, tables, and metadata from PDF documents with high accuracy
- **OCR Engine** - Convert images and scanned documents to machine-readable text

### Text Analytics
- **Summarization** - Generate concise summaries from long-form text content
- **Content Tagging** - Automatically extract and assign relevant tags to text

## Key Features

- **Containerized Deployment** - Each component runs in its own Docker container for easy deployment and scaling
- **RESTful APIs** - Simple HTTP interfaces for seamless integration
- **Configuration Management** - Environment-based configuration for different deployment scenarios
- **Health Monitoring** - Built-in health checks and monitoring endpoints

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-components
   ```

2. **Choose your components**
   ```bash
   # Start individual components
   docker-compose up summarization-service
   docker-compose up pdf-parser-service
   ```

3. **Use the APIs**
   ```bash
   # Example: Summarize text
   curl -X POST http://localhost:8080/v1/summarize \
     -H "Content-Type: application/json" \
     -d '{"text": "Your long text here..."}'
   ```

## Requirements

- Docker and Docker Compose
- Python 3.10+ (for local development)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for details on how to submit improvements, bug fixes, and new components.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.
