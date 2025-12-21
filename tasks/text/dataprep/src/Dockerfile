# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.12-slim

ENV LANG=C.UTF-8

ARG ARCH="cpu"

RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    libcairo2 \
    google-perftools \
    libgoogle-perftools-dev \
    wget curl \
    git \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user && \
    chown -R user:user /home/user

COPY __init__.py /home/user/AIComps/__init__.py
COPY tasks/version.py /home/user/AIComps/tasks/version.py
COPY tasks/cores /home/user/AIComps/tasks/cores
COPY tasks/text/dataprep /home/user/AIComps/tasks/text/dataprep

ARG uvpip='uv pip install --system --no-cache-dir'
RUN pip install --no-cache-dir --upgrade pip setuptools uv && \
    $uvpip torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu && \
    $uvpip -r /home/user/AIComps/tasks/text/dataprep/src/requirements-cpu.txt && \
    $uvpip intel-extension-for-pytorch==2.8.0

ENV PYTHONPATH="/home/user:${PYTHONPATH}"
ENV LD_PRELOAD="/lib/x86_64-linux-gnu/libtcmalloc.so.4"

RUN mkdir -p /home/user/AIComps/tasks/text/dataprep/src/uploaded_files && chown -R user:user /home/user/AIComps/tasks/text/dataprep/src/uploaded_files
RUN mkdir -p /data && chown -R user:user /data

RUN mkdir -p /usr/local/lib/python3.12/site-packages/static && \
    chown -R user:user /usr/local/lib/python3.12/site-packages/static

ENV NLTK_DATA=/home/user/nltk_data \
    HF_HUB_CACHE=/data \
    XDG_CACHE_HOME=/home/user/.cache

RUN mkdir -p /home/user/AIComps/tasks/text/dataprep/src/out && \
    chown -R user:user /home/user/AIComps/tasks/text/dataprep/src/out

USER user

WORKDIR /home/user/AIComps/tasks/text/dataprep/src

ENTRYPOINT ["sh", "-c", "python $( [ \"$MULTIMODAL_DATAPREP\" = \"true\" ] && echo 'opea_dataprep_multimodal_microservice.py' || echo 'opea_dataprep_microservice.py')"]
