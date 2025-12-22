# ASR API Endpoint

## Setup

1. Create and the environment 
    ```uv sync```
2. Select tcmalloc as the memory allocator
    ```
    sudo apt-get install google-perftools
   
    export LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4"```
    
3. export the envs
    - INPUT_LANGUAGES=hindi
    - ASR_PAD_OFFSET=200000
    - DEFAULT_SAMPLING_RATE=16000
    

3. Run the server
    `uvicorn main:app --host 0.0.0.0 --port 8000`

## Docker 

1. Build the image
```
docker build --build-arg HTTP_PROXY=$HTTP_PROXY --build-arg http_proxy=$http_proxy --build-arg HTTPS_PROXY=$HTTPS_PROXY --build-arg https_proxy=$https_proxy -f Dockerfile -t asr_openai:0.1 .
```

2. Run the container
```
docker run -it --runtime=habana -e HABANA_VISIBLE_DEVICES=4 -e http_proxy=$http_proxy -e https_proxy=$https_proxy --net=host --ipc=host asr_openai:0.1
```

## Testing

- curl
```curl
curl http://localhost:8000/v1/audio/transcriptions \
  -H "Authorization: Bearer None" \
  -H "Content-Type: multipart/form-data" \
  -F file="@/path/to/file/audio.mp3" \
  -F model="wav2vec"
```

- openai python sdk
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="none")
audio_file= open("audio.wav", "rb")

transcription = client.audio.transcriptions.create(
    model="wav2vec", 
    file=audio_file
)

print(transcription.text)

```