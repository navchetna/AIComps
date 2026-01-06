# Svara TTS (vLLM)

This guide provides instructions to set up and run the Svara TTS (Text-to-Speech) model using vLLM.

---

## Setup

### Step 1: Clone the vLLM-TTS Repository

```bash
cd AIComps/tasks/speech/text2speech/svara
git clone https://github.com/AdityaKulshrestha/vllm-audio
```

### Step 2: Navigate to the vLLM-TTS Directory

```bash
cd vllm-audio/
```

### Step 3: Build the Docker Image

```bash
docker build -f docker/Dockerfile.cpu \
  --build-arg VLLM_CPU_AMXBF16=true \
  --build-arg VLLM_CPU_AVX512BF16=true \
  --tag vllm-cpu-env \
  --target vllm-openai .
```

### Step 4: Run the Docker Container

```bash
sudo docker run --rm -p 8000:8000 \
  --shm-size 4g \
  -e VLLM_CPU_OMP_THREADS_BIND="0-31" \
  -e VLLM_CPU_KVCACHE_SPACE=40 \
  --name vllm-tts \
  -v /data/hf_cache:/root/.cache/ \
  vllm-cpu-env kenpath/svara-tts-v1 \
  --dtype=bfloat16 \
  --audio_encodec snac \
  --max-num-seqs 2048
```

---

## Testing the API

### Using cURL

```bash
curl -X POST "http://localhost:8000/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -o output.wav \
  -d '{
    "model": "kenpath/svara-tts-v1",
    "input": "मी खूप दिवसांनी तुझ्याशी बोललो नाही, आणि तुझ्याबद्दल खूप काही विचार करत होतो, म्हणून मी तुझाला हे पत्र लिहिण्याचा निर्णय घेतला.",
    "voice": "Marathi (Male)",
    "response_format": "wav",
    "speed": 1,
    "stream": false
  }'
```

### Using OpenAI Python Client

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1")

response = client.audio.speech.create(
    model="kenpath/svara-tts-v1",
    input="मी खूप दिवसांनी तुझ्याशी बोललो नाही, आणि तुझ्याबद्दल खूप काही विचार करत होतो, म्हणून मी तुझाला हे पत्र लिहिण्याचा निर्णय घेतला.",
    voice="Marathi (Male)",
    response_format="wav",
    speed=1,
    stream=False
)

with open("output.wav", "wb") as f:
    f.write(response)
```

---

## API Parameters

- **model**: The TTS model to use (`kenpath/svara-tts-v1`)
- **input**: The text to convert to speech (supports Marathi and other Indic languages)
- **voice**: Voice type (e.g., `Marathi (Male)`)
- **response_format**: Audio output format (`wav`)
- **speed**: Speech speed multiplier (default: `1`)
- **stream**: Enable streaming response (`true` or `false`)