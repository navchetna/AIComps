
# TTS API Endpoint


## Setup

1. Create environment and install dependencies
    ```uv sync```
2. Clone the directory and download the models:
    `./setup.sh`
3. Enter the cloned repo
    `cd Fastspeech2_HS`
4. Run the server
    `uvicorn main:app --host 0.0.0.0 --port 8000`


NOTE - For error like this, run the server from within the Fastspeech2_HS directory
```
  File "/usr/local/lib/python3.10/dist-packages/habana_frameworks/torch/core/__init__.py", line 106, in wrapper
    ret = original_fn(*args, **kwargs)
ModuleNotFoundError: No module named 'text_preprocess_for_inference'
```

## Docker 

1. Setup
```bash
docker build -f Dockerfile -t tts_openai:0.1 .
```

2. Run the container
```bash
docker run -d -p 8000:8000 --name fastspeech2_hs tts_openai:0.1
```

## Testing

- curl
```bash
curl http://localhost:8000/v1/audio/speech  -H "Authorization: Bearer any_value"   -H "Content-Type: application/json"  -d '{
    "model": "fastspeech2", 
    "input": "बहुत पुरानी बात है एक गांव में शेखर नाम का एक व्यक्ति रहता था।",
    "voice": "male" 
  }'  --output speech.mp3
```

- openai python sdk
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