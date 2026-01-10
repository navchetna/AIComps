FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    google-perftools \
    libgoogle-perftools-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up TCMalloc for memory optimization
ENV LD_PRELOAD=/lib/x86_64-linux-gnu/libtcmalloc.so.4

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using UV
RUN uv pip install --system -r requirements.txt

# Install marker-pdf library
RUN uv pip install --system git+https://github.com/navchetna/marker.git

# Install Surya fork (optimized)
RUN uv pip install --system git+https://github.com/navchetna/surya.git

# Install tree parser
RUN uv pip install --system git+https://github.com/navchetna/tree-parser.git

# Install Intel Extension for PyTorch (for Xeon CPU optimization)
RUN uv pip install --system intel_extension_for_pytorch==2.8.0

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /app/outputs

# Expose port
EXPOSE 8000

# Run the FastAPI server
CMD ["python", "server.py"]
