# vLLM Deployment on CPUs

This guide provides instructions for deploying vLLM on CPU infrastructure using Docker. Refer to the [Official docs](https://docs.vllm.ai/en/stable/getting_started/installation/cpu/#faq) for more information.

### Prerequisites
- Docker installed and configured

# Installation Methods

## Method 1: Set up using Python

**Create a new Python environment:**

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
```

**Install recommended compiler:**

We recommend using `gcc/g++ >= 12.3.0` as the default compiler to avoid potential problems. For example, on Ubuntu 22.4, you can run:
```bash
sudo apt-get update -y
sudo apt-get install -y gcc-12 g++-12 libnuma-dev python3-dev
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 10 --slave /usr/bin/g++ g++ /usr/bin/g++-12
```

**Clone the vLLM project:**

```bash
git clone https://github.com/vllm-project/vllm.git vllm_source
cd vllm_source
```

**Install the required dependencies:**

```bash
uv pip install -r requirements/cpu-build.txt --torch-backend cpu
uv pip install -r requirements/cpu.txt --torch-backend cpu
```

**Build and install vLLM:**

```bash
VLLM_TARGET_DEVICE=cpu uv pip install . --no-build-isolation
```

If you want to ***develop*** vLLM, install it in editable mode instead:

```bash
VLLM_TARGET_DEVICE=cpu uv pip install -e . --no-build-isolation
```

**Launch a vLLM service on CPU:**

```bash
export VLLM_CPU_KVCACHE_SPACE=40
export VLLM_CPU_OMP_THREADS_BIND=0-30
vllm serve Qwen/Qwen3-4B-Instruct-2507 --dtype=bfloat16
```

We recommend configuring tensor-parallel-size to match the number of NUMA nodes on your system. Note that the current release does not support tensor-parallel-size=6. To determine the number of NUMA nodes available, use the following command:

```bash
lscpu | grep "NUMA node(s):" | awk '{print $3}'
```

## Method 2: Build docker image from source

**Clone the repository and build the Docker image:**

```bash
git clone https://github.com/vllm-project/vllm.git
cd vllm

# Use the most stable version
git fetch --tags
git checkout v0.13.0

# Build the image
docker build -f docker/Dockerfile.cpu \
    --build-arg VLLM_CPU_AVX512BF16=true \
    --build-arg VLLM_CPU_AVX512VNNI=true \
    --tag vllm-cpu-env \
    --target vllm-openai .
```

### Running the vLLM Server

Launch the vLLM server with the following command:

```bash
docker run -d -p 8000:8000 \
    --security-opt seccomp=unconfined \
    --cap-add SYS_NICE \
    --shm-size=4g \
    -e VLLM_CPU_KVCACHE_SPACE=<KV cache space> \
    -e VLLM_CPU_OMP_THREADS_BIND=<CPU cores for inference> \
    -e VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 \
    -e LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4:" \
    -e TORCHINDUCTOR_COMPILE_THREADS=1 \
    -e VLLM_CPU_SGL_KERNEL=1 \
    vllm-cpu-env \
    --model=Qwen/Qwen3-4B-Instruct-2507 \
    --dtype=bfloat16 \
    --distributed-executor-backend mp \
    --host 0.0.0.0 \
    --port 8000 \
    --swap-space 40 \
    --max-num-seqs 4096 \
    --max-num-batched-tokens 4096 \
    -O3 \
    --disable-sliding-window
```

## Test the API

After the server is running, you can hit the OpenAI-compatible completions endpoint with curl:

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen3-4B-Instruct-2507",
        "messages": [
            {"role": "user", "content": "San Francisco is a"}
        ],
        "max_tokens": 7,
        "temperature": 0
    }'
```

## Environment Variables

### VLLM_CPU_KVCACHE_SPACE

Specifies the KV Cache size in GiB (e.g., `VLLM_CPU_KVCACHE_SPACE=40` allocates 40 GiB). Larger values allow vLLM to run more requests in parallel. Configure based on hardware capabilities and memory management requirements.

**Default:** 0

### VLLM_CPU_OMP_THREADS_BIND

Defines CPU cores dedicated to OpenMP threads. Can be set as:
- CPU ID lists: `0-31` (32 threads on cores 0-31)
- Multiple ranks: `0-31|32-63` (rank0 on cores 0-31, rank1 on cores 32-63)
- `auto` (default): Binds threads to CPU cores in each NUMA node
- `nobind`: Disables binding, uses `OMP_NUM_THREADS` variable

**Default:** auto

### VLLM_CPU_NUM_OF_RESERVED_CPU

Specifies the number of CPU cores not dedicated to OpenMP threads per rank. Only effective when `VLLM_CPU_OMP_THREADS_BIND` is set to `auto`.

**Default:** None (no reserved CPUs for world_size==1, 1 CPU per rank for world_size>1)

### CPU_VISIBLE_MEMORY_NODES

Specifies visible NUMA memory nodes for vLLM CPU workers (similar to `CUDA_VISIBLE_DEVICES`). Only effective when `VLLM_CPU_OMP_THREADS_BIND` is set to `auto`. Provides control for auto thread-binding, including masking nodes and changing binding sequences.

### VLLM_CPU_SGL_KERNEL

Enables small-batch optimized kernels for linear and MoE layers, ideal for low-latency online serving. Requires AMX instruction set, BFloat16 weight type, and weight shapes divisible by 32. Recommended for low concurrency/batch size scenarios.

**Recommended:** Set to 1 for optimal performance with low concurrency

### VLLM_ALLOW_LONG_MAX_MODEL_LEN

Allows specifying a max sequence length greater than the model's config.json value.

**Usage:** Set `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` to enable

### TORCHINDUCTOR_COMPILE_THREADS

Controls the number of threads used for PyTorch Inductor compilation, affecting compilation parallelism and speed.

**Recommended:** `TORCHINDUCTOR_COMPILE_THREADS=1`

### LD_PRELOAD

Enables TCMalloc for improved memory allocation performance. TCMalloc provides per-thread caches for faster malloc/free operations, reduces fragmentation and RSS usage, and supports huge pages for NUMA-aware inference.

**Recommended:** `LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4:"`

## Configuration Guidelines

- Adjust `VLLM_CPU_KVCACHE_SPACE` based on available system memory
- Configure `VLLM_CPU_OMP_THREADS_BIND` according to your CPU topology
- Enable `VLLM_CPU_SGL_KERNEL` for low-latency serving scenarios
- Use TCMalloc (`LD_PRELOAD`) for optimal memory management