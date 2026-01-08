# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-slim

ENV LANG=C.UTF-8

RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    git \
    libjemalloc-dev

RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user && \
    chown -R user /home/user/

COPY tasks/__init__.py /home/AIComps/tasks/__init__.py
COPY tasks/version.py /home/AIComps/tasks/version.py
COPY tasks/cores /home/AIComps/tasks/cores
COPY __init__.py /home/AIComps/__init__.py
COPY models/rerankings/src/ /home/AIComps/models/rerankings/src/

ARG uvpip='uv pip install --system --no-cache-dir'
RUN pip install --no-cache-dir --upgrade pip setuptools uv && \
    $uvpip torch --index-url https://download.pytorch.org/whl/cpu && \
    $uvpip -r /home/AIComps/models/rerankings/src/requirements-cpu.txt

ENV PYTHONPATH=$PYTHONPATH:/home/

USER user

WORKDIR /home/AIComps/models/rerankings/src/

ENTRYPOINT ["python", "opea_reranking_microservice.py"]
