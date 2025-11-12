# Dataprep Microservice

The Dataprep Microservice aims to preprocess the data from various sources (either structured or unstructured data) to text data, and convert the text data to embedding vectors then store them in the database.

## Table of contents

1. [Install Requirements](#install-requirements)
2. [Dataprep Microservice on Various Databases](#dataprep-microservice-on-various-databases)
3. [Running in the air gapped environment](#running-in-the-air-gapped-environment)

## Install Requirements

```bash
apt-get update
apt-get install libreoffice
```

## Dataprep Microservice on Various Databases

Dataprep microservice are supported on various databases, as shown in the table below, for details, please refer to the respective readme listed below.

| Databases               | Readme                                                                   |
| :---------------------- | :----------------------------------------------------------------------- |
| `Qdrant`                | [Dataprep Microservice with Qdrant](src/README_qdrant.md)                |

## Running in the air gapped environment

The following steps are common for running the dataprep microservice in an air gapped environment (a.k.a. environment with no internet access), for all DB backends.

1. Download the following models, e.g. `huggingface-cli download --cache-dir <model data directory> <model>`

- microsoft/table-transformer-structure-recognition
- timm/resnet18.a1_in1k
- unstructuredio/yolo_x_layout

2. launch the `dataprep` microservice with the following settings:

- mount the `model data directory` as the `/data` directory within the `dataprep` container
- set environment variable `HF_HUB_OFFLINE` to 1 when launching the `dataprep` microservice

e.g. `docker run -d -v <model data directory>:/data -e HF_HUB_OFFLINE=1 ... ...`
