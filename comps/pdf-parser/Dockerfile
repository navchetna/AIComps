FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for building packages and optional TCMalloc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git \
      curl \
      build-essential \
      libgl1 \
      google-perftools \
      libgoogle-perftools-dev && \
    rm -rf /var/lib/apt/lists/*


# Install Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install git+https://github.com/navchetna/marker.git@main && \
    pip install --upgrade git+https://github.com/navchetna/marker.git@main && \
    pip install git+https://github.com/navchetna/surya.git && \
    pip install git+https://github.com/navchetna/tree-parser.git@alt && \
    pip install intel_extension_for_pytorch==2.8.0

# Copy application files into the image.
COPY . .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

# TCMalloc can be enabled by keeping the following env var.
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4


ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["marker_server", "--host", "0.0.0.0", "--port", "8000"]

