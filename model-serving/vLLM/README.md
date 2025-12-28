
# vLLM on CPU 

This vLLM installation guide walks you through building and serving **vLLM** on **CPU** with a fast **uv**-managed Python environment, recommended compilers, memory allocator tuning (TCMalloc), and a quick test against the OpenAI‑compatible `/v1/chat/completions` endpoint using **Qwen2.5‑1.5B‑Instruct**.

---

## 1) Prerequisites

- **OS:** Linux (e.g., Ubuntu/Debian)
- **Python:** 3.12 
- **Compiler:** GCC/G++ ≥ 12.3
- **CPU features:** AVX512 recommended on x86; AVX512_BF16 (optional) further improves BF16. Use `lscpu` to check flags. 
- **PyTorch (CPU wheel)**

---

## 2) Create and activate a **uv** virtual environment (Python 3.12)

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
```

---

## 3) Install the recommended compiler toolchain

```bash
sudo apt-get update -y
sudo apt-get install -y gcc-12 g++ libnuma-dev
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 10 --slave /usr/bin/g++ g++ /usr/bin/g++-12
```

GCC 12+ helps avoid build issues for vLLM’s CPU backend; `libnuma-dev` enables NUMA‑aware builds.

---

## 4) Clone **vLLM**

```bash
git clone https://github.com/vllm-project/vllm.git vllm_source
cd vllm_source
```
---

## 5) Install CPU build dependencies and runtime requirements

**Files inside `requirements/` (e.g., `cpu-build.txt`, `cpu.txt`):**

```bash
uv pip install -v -r requirements/cpu-build.txt --index-url https://download.pytorch.org/whl/cpu
uv pip install -v -r requirements/cpu.txt --index-url https://download.pytorch.org/whl/cpu
```


---

## 6) Build and install vLLM for **CPU**

```bash
VLLM_TARGET_DEVICE=cpu uv pip install . --no-build-isolation
```

Setting `VLLM_TARGET_DEVICE=cpu` ensures the build selects the CPU backend.

> **Dtype note:** The CPU backend prefers **BF16** by default (FP16 gets cast to BF16). AVX512_BF16 enables native BF16 and improves performance if present.

---

## 7) Install **TCMalloc** and set `LD_PRELOAD`

1) Install the allocator:

```bash
sudo apt-get update
sudo apt-get install -y libtcmalloc-minimal4
```

2) Discover paths :

```bash
# TCMalloc
find /usr/lib -name "libtcmalloc_minimal.so.4" 2>/dev/null

# Intel OpenMP (usually bundled in the torch CPU wheel)
find .venv -name "libiomp5.so" 2>/dev/null
```

3) Export `LD_PRELOAD` combining the TCMalloc and Intel OpenMP libraries:

```bash
export LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4:/path/to/venv/site-packages/torch/lib/libiomp5.so:$LD_PRELOAD"
```

TCMalloc can reduce memory overhead and improve allocator performance; the exact `.so` path varies by distro and version.

> If you see `cannot be preloaded` errors, re‑check the actual `.so` version installed (e.g., `.so.4.5.9` on Ubuntu 22.04) and use that path.

---

## 8) Runtime tuning: KV‑cache and OpenMP thread binding

```bash
export VLLM_CPU_KVCACHE_SPACE=40            
# GB reserved for KV cache
export VLLM_CPU_OMP_THREADS_BIND=0-30       
# bind OMP worker threads to CPU cores
```

- `VLLM_CPU_KVCACHE_SPACE` sets the KV cache size (in **GB**); larger values enable more concurrency but raise memory usage.
- `VLLM_CPU_OMP_THREADS_BIND` lets you pin OpenMP threads to specific cores (ranges or comma‑lists).


---

## 9) Launch **vLLM** (OpenAI‑compatible server) on CPU

```bash
vllm serve "Qwen/Qwen2.5-1.5B-Instruct" \
  --dtype bfloat16 \
  --max-model-len 4096
```

The vLLM server provides OpenAI‑compatible routes (`/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, etc.).

---

## 10) Test the server

Use `curl` against the **OpenAI‑compatible** Chat Completions API:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "messages": [
      {"role": "system", "content": "You are a helpful coding assistant."},
      {"role": "user", "content": "Write a quick Python function to calculate Fibonacci numbers."}
    ]
  }'
```

---

## Troubleshooting & Tips

- **Check CPU flags**: `lscpu | grep -i avx512` to confirm AVX512 support; if absent, expect lower performance and prefer `--dtype float32`.
- **Missing `libiomp5.so`**: It’s typically bundled with the Torch CPU wheel under `site-packages/torch/lib/`. Use `find .venv -name libiomp5.so`.
- **Allocator path errors**: Use the exact library path/version for `libtcmalloc_minimal.so.*` per distro. 
- **Choose the right PyTorch backend/index**: uv’s PyTorch guide shows how to pin CPU or CUDA indices and avoid mismatches. 
- **Server arguments**: Explore `vllm serve --help=listgroup` or docs for advanced flags (tensor parallel, quantization, generation config). 

---
