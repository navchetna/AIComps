# TTS API Endpoint

This guide provides instructions for setting up and testing a Text-to-Speech (TTS) API endpoint using FastSpeech2_HS.

---

## Setup Methods

### Method 1: Uvicorn Setup

#### Step 1: Create Environment and Install Dependencies

```bash
cd AIComps/tasks/speech/text2speech/fastspeech2_HS
uv sync
source .venv/bin/activate
```

#### Step 2: Download the Models

```bash
bash setup.sh
```

#### Step 3: Enter the Cloned Repository

```bash
cd Fastspeech2_HS
```

#### Step 4: Run the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Note:** If you encounter a `ModuleNotFoundError: No module named 'text_preprocess_for_inference'`, run the server from within the `Fastspeech2_HS` directory.

---

### Method 2: Docker Setup

#### Step 1: Build the Image

```bash
docker build -f Dockerfile -t tts_openai:0.1 .
```

#### Step 2: Run the Container

```bash
docker run --rm -d -p 8000:8000 --name fastspeech2_hs tts_openai:0.1
```

---

## Testing the API

### Using cURL

```bash
curl http://localhost:8000/v1/audio/speech \
  -H "Authorization: Bearer any_value" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "fastspeech2", 
    "input": "बहुत पुरानी बात है एक गांव में शेखर नाम का एक व्यक्ति रहता था।",
    "voice": "male" 
  }' \
  --output speech.mp3
```

### Using OpenAI Python SDK

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="None")
speech_file_path = Path(__file__).parent / "tts_audio.wav"

with client.audio.speech.with_streaming_response.create(
    model="fastspeech2",
    input="बहुत पुरानी बात है एक गांव में शेखर नाम का एक व्यक्ति रहता था।",
    voice="female",
    instructions="hindi"
) as response:
    response.stream_to_file(speech_file_path)
```

---

## API Parameters

- **model**: The TTS model to use (e.g., `fastspeech2`)
- **input**: The text to convert to speech (supports Hindi text)
- **voice**: Voice type (`male` or `female`)
- **instructions**: Language specification (e.g., `hindi`)