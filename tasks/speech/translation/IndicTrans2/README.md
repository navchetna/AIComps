# Translate API

This guide provides instructions to set up and run the IndicTrans2 Translation API.

---

## Setup

### Step 1: Clone the IndicTransToolkit Repository

```bash
cd AIComps/tasks/speech/translation/IndicTrans2
git clone https://github.com/VarunGumma/IndicTransToolkit
```

### Step 2: Install the Toolkit

```bash
uv sync && source .venv/bin/activate

cd IndicTransToolkit && \
git checkout 728a7a9e8bcbbc59ca9e15c4297889df866b8c4a && \
uv pip install --editable .
```

### Step 3: Install Dependencies

```bash
uv pip install -r requirements.txt
```

### Step 4: Run the Server

> This translation model is gated, please gain access and then export your token: *[IndicTrans2 Model Card](https://huggingface.co/ai4bharat/indictrans2-indic-indic-1B)*
```bash
cd ..
export HF_TOKEN=<your_token>
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Notes:**
- The warmup takes time, so please wait for the server to start completely.
- If memory usage is too high, try reducing the batch size during model initialization.

---

## Docker Setup

### Build the Docker Image

```bash
cd AIComps/tasks/speech/translation/IndicTrans2
docker build -t indictrans2 .
```

### Run the Docker Container

```bash
docker run -d -p 8000:8000 \
-e HF_TOKEN=$HF_TOKEN \
--name indictrans2 \
indictrans2
```

---

## Testing the API

### Using cURL

```bash
curl -X 'POST' \
  'http://localhost:8000/translation/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "src_lang": "hin_Deva",
    "tgt_lang": "mal_Mlym",
    "text": "मेरे मित्र ने मुझे उसके जन्मदिन की पार्टी में बुलाया है, और मैं उसे एक तोहफा दूंगा।"
  }'
```

### Using Python

```python
import requests

# The URL of the API endpoint
url = "http://localhost:8000/translation/"

# The data payload to be sent as a JSON body
payload = {
    "src_lang": "hin_Deva",
    "tgt_lang": "mal_Mlym",
    "text": "मेरे मित्र ने मुझे उसके जन्मदिन की पार्टी में बुलाया है, और मैं उसे एक तोहफा दूंगा।"
}

# The headers for the request
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

try:
    # Send the POST request
    response = requests.post(url, headers=headers, json=payload)
    
    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status()
    
    # Print the server's response
    print("Request successful!")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

except requests.exceptions.RequestException as e:
    # Handle potential network errors (e.g., connection refused)
    print(f"An error occurred: {e}")
```

---

## API Parameters

- **src_lang**: Source language code (e.g., `hin_Deva` for Hindi in Devanagari script)
- **tgt_lang**: Target language code (e.g., `mal_Mlym` for Malayalam in Malayalam script)
- **text**: The text to be translated

### Supported Language Codes

IndicTrans2 supports multiple Indic languages. Language codes follow the format `{language}_{script}`. For example:
- `hin_Deva` - Hindi (Devanagari)
- `mal_Mlym` - Malayalam (Malayalam script)
- `ben_Beng` - Bengali (Bengali script)
- `tam_Taml` - Tamil (Tamil script)

Refer to the [IndicTransToolkit documentation](https://github.com/VarunGumma/IndicTransToolkit) for a complete list of supported language codes.