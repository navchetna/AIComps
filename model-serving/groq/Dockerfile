FROM python:3.11-slim AS base

# get security updates
RUN apt-get update && apt-get upgrade -y && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/user

RUN useradd -m -s /bin/bash user && \
  mkdir -p $HOME && \
  chown -R user $HOME

# Copy the application code into the container
COPY comps/__init__.py /home/user/comps/__init__.py
COPY comps/version.py /home/user/comps/version.py
COPY comps/cores /home/user/comps/cores
COPY comps/groq /home/user/comps/groq

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r /home/user/comps/groq/requirements.txt

ENV PYTHONPATH=/home/user


WORKDIR /home/user/comps/groq

ENTRYPOINT ["python", "main.py"]