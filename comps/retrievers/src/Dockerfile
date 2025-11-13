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

COPY comps/__init__.py /home/user/comps/__init__.py
COPY comps/version.py /home/user/comps/version.py
COPY comps/cores /home/user/comps/cores
COPY comps/retrievers /home/user/comps/retrievers

ARG uvpip='uv pip install --system --no-cache-dir'
RUN pip install --no-cache-dir --upgrade pip setuptools uv && \
      $uvpip torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu; \
      $uvpip -r /home/user/comps/retrievers/src/requirements-cpu.txt;

ENV PYTHONPATH=$PYTHONPATH:/home/user

USER user

WORKDIR /home/user/comps/retrievers/src

ENTRYPOINT ["python", "opea_retrievers_microservice.py"]
