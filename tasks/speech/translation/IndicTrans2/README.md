# Translate API


## Setup


1. `git clone https://github.com/VarunGumma/IndicTransToolkit`
2. `cd IndicTransToolkit && git checkout 728a7a9e8bcbbc59ca9e15c4297889df866b8c4a && pip install --editable .`
3. `pip install -r requirements.txt`
4. `uvicorn main:app --host 0.0.0.0 --port 8000`

NOTE - 
1. The warmup takes time, hence please wait for the server to start.
2. If the memory explodes, try reducing the batch size during model initialization.

## Docker

### Build Docker Image
```bash
docker build -t indictrans2 .
```

### Run Docker Container
```bash
docker run -d -p 8000:8000 -e HF_TOKEN=$HF_TOKEN --name indictrans2 indictrans2
```


## Testing

- curl
```curl
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

- python 
```
import requests
import json

# The URL of the API endpoint
url = "http://localhost:8000/translation/"

# The data payload to be sent as a JSON body
# Python dictionaries are automatically converted to JSON by the requests library.
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