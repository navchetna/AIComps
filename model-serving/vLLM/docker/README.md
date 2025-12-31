# vLLM Performance Guide for Intel® Xeon® 6 (using Docker)

This guide provides an optimized workflow for deploying vLLM on Intel® Xeon® 6 processors. It leverages **Intel® Advanced Matrix Extensions (AMX)** and **AVX-512** to achieve up to **2x throughput improvement** over standard installations.

## Prerequisites

- Docker installed and configured
- Model Access: This guide uses `Qwen/Qwen2.5-1.5B-Instruct`. If you choose to use gated models (e.g., Llama 3.2), ensure you have requested access on Hugging Face and have a valid Access Token.
- Architecture: Optimized for Intel Xeon 6 (Granite Rapids) with SNC3 (Sub-NUMA Clustering) enabled.

## Installation Methods

### Optimized Docker Build

Standard builds often disable AVX-512 by default. Use the following command to explicitly enable **AMX** and **AVX-512** support:

```bash
# Build from the root of the vLLM source directory
docker build -f docker/Dockerfile.cpu \
    --build-arg PYTHON_VERSION=3.12 \
    --build-arg VLLM_CPU_AVX512BF16=true \
    --build-arg VLLM_CPU_AVX512VNNI=true \
    --build-arg VLLM_CPU_AMXBF16=true \
    --build-arg VLLM_CPU_DISABLE_AVX512=false \
    --build-arg max_jobs=$(nproc) \
    --tag vllm-xeon-img \
    --target vllm-openai .
```

## Running the vLLM Server

Launch the vLLM server with NUMA pinning and CPU affinity:

```bash
docker run -d -p 8000:8000 \
    --name vllm-xeon \
    --security-opt seccomp=unconfined \
    --cap-add SYS_NICE \
    --shm-size=64g \
    --cpuset-cpus="0-47" \
    --cpuset-mems="0-2" \
    -v /mnt/vllm_models:/root/.cache/huggingface \
    -e VLLM_CPU_KVCACHE_SPACE=100 \
    -e VLLM_USE_V1=1 \
    -e VLLM_CPU_SGL_KERNEL=1 \
    -e OMP_NUM_THREADS=48 \
    -e VLLM_CPU_OMP_THREADS_BIND="0-47" \
    -e LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4" \
    -e TORCHINDUCTOR_COMPILE_THREADS=1 \
    vllm-xeon-img \
    --model Qwen/Qwen2.5-1.5B-Instruct \
    --dtype bfloat16 \
    --enforce-eager \
    --distributed-executor-backend mp \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 4096 \
    --disable-sliding-window
```

## Key Performance Variables

| Variable | Description |
| --- | --- |
| `--cpuset-mems="0-2"` | Binds memory to Node 0 (Local Socket), avoiding the 21ms remote-fetch penalty. |
| `VLLM_USE_V1=1` | Enables the new vLLM V1 engine for improved CPU scheduling. |
| `VLLM_CPU_SGL_KERNEL=1` | Activates optimized CPU-specific attention kernels. |
| `LD_PRELOAD` | Uses `TCMalloc` for more efficient memory allocation at high core counts. |

## Test the API

After the server is running, you can hit the OpenAI-compatible completions endpoint with curl:

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "prompt": "What is prospect theory?",
        "max_tokens": 300,
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
---
