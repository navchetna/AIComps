# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-slim

ARG ARCH="cpu"

RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    libcairo2 \
    libglib2.0-0 \
    libjemalloc-dev \
    wget curl \
    build-essential

RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user && \
    chown -R user /home/user/

COPY __init__.py /home/user/AIComps/__init__.py
COPY tasks/__init__.py /home/user/AIComps/tasks/__init__.py
COPY tasks/version.py /home/user/AIComps/tasks/version.py
COPY tasks/cores /home/user/AIComps/tasks/cores
COPY tasks/text/retrievers /home/user/AIComps/tasks/text/retrievers


ARG uvpip='uv pip install --system --no-cache-dir'
RUN pip install --no-cache-dir --upgrade pip setuptools uv && \
    $uvpip torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu; \
    $uvpip -r /home/user/AIComps/tasks/text/retrievers/src/requirements-cpu.txt;

ENV PYTHONPATH=/home/user

USER user

WORKDIR /home/user/AIComps/tasks/text/retrievers/src

ENTRYPOINT ["python", "opea_retrievers_microservice.py"]
