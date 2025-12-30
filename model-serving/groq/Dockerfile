FROM python:3.11-slim AS base

# get security updates
RUN apt-get update && apt-get upgrade -y && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/user

RUN useradd -m -s /bin/bash user && \
  mkdir -p $HOME && \
  chown -R user $HOME

# Copy the application code into the container
COPY __init__.py /home/user/AIComps/__init__.py
COPY tasks /home/user/AIComps/tasks
COPY model-serving/groq /home/user/AIComps/model-serving/groq

RUN pip install --no-cache-dir --upgrade pip setuptools && \
  pip install --no-cache-dir -r /home/user/AIComps/model-serving/groq/requirements.txt

ENV PYTHONPATH=/home/user

WORKDIR /home/user/AIComps/model-serving/groq

ENTRYPOINT ["python", "main.py"]