# ASR Model deployment using Servoc


## Setup
1. Clone the Servoc repository
    ```bash
    https://github.com/AdityaKulshrestha/Servoc.git
    ```
2. Create virtual environment and install dependencies
    ```bash
    cd Servoc
    uv sync --group springlab-wav2vec2
    ```
3. Activate the virtual environment
    ```bash
    source .venv/bin/activate
    ```
4. Run the server
    ```bash
    python main.py
    ```

## Test the ASR model


### Using cURL
You can test the deployed ASR model using the following cURL command:
```bash
curl -X POST "http://localhost:8080/v1/audio/transcriptions" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@../sample.wav" -F "model=wav2vec2"
```

### Using Python script (OpenAI Client)
You can also use the following Python script to test the ASR model:
```python
import openai
openai.api_base = "http://localhost:8080/v1"
openai.api_key = "your_api_key"

audio_file_path = "path_to_your_audio_file.wav"

with open(audio_file_path, "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        model="wav2vec2",
        file=audio_file
    )       
print(transcript)
```


## Important Notes
1. If the port is already in use, you can change it by modifying the `port` variable under ServerConfig in the `Servoc/app/config.py` file.
