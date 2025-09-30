# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.12-slim

ENV LANG=C.UTF-8

ARG ARCH="cpu"

RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    default-jre \
    libcairo2 \
    libjemalloc-dev \
    libmariadb-dev \
    libpq-dev \
    libreoffice \
    poppler-utils \
    tesseract-ocr \
    ffmpeg \
    wget curl \
    git \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user && \
    chown -R user:user /home/user

COPY comps /home/user/comps

ARG uvpip='uv pip install --system --no-cache-dir'
RUN pip install --no-cache-dir --upgrade pip setuptools uv && \
    $uvpip torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    $uvpip -r /home/user/comps/dataprep/src/requirements-cpu.txt

ENV PYTHONPATH="/home/user:${PYTHONPATH}"

RUN mkdir -p /home/user/comps/dataprep/src/uploaded_files && chown -R user:user /home/user/comps/dataprep/src/uploaded_files
RUN mkdir -p /data && chown -R user:user /data

RUN mkdir -p /usr/local/lib/python3.12/site-packages/static && \
    chown -R user:user /usr/local/lib/python3.12/site-packages/static

ENV NLTK_DATA=/home/user/nltk_data \
    HF_HUB_CACHE=/data \
    XDG_CACHE_HOME=/home/user/.cache

RUN mkdir -p /home/user/comps/dataprep/src/out && \
    chown -R user:user /home/user/comps/dataprep/src/out

USER user

RUN mkdir -p /home/user/nltk_data && \
    python -m nltk.downloader -d /home/user/nltk_data punkt_tab averaged_perceptron_tagger_eng stopwords

WORKDIR /home/user/comps/dataprep/src

ENTRYPOINT ["sh", "-c", "python $( [ \"$MULTIMODAL_DATAPREP\" = \"true\" ] && echo 'opea_dataprep_multimodal_microservice.py' || echo 'opea_dataprep_microservice.py')"]
