
import os
import requests

# Configuration
pdf_path = "/home/intel/Ervin/Test/2305.15032v1-2-3.pdf"
user = "ervin"

pdf_parsing_url = "http://localhost:8001/marker/upload"
dataprep_ingest_url = "http://localhost:5000/v1/dataprep/ingest"
collection_name = "test_collection"

# Step 1: Upload the PDF for parsing
with open(pdf_path, 'rb') as f:
    files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
    data = {'user': user}
    print(f"Uploading PDF for parsing: {pdf_path}")
    response = requests.post(pdf_parsing_url, files=files, data=data)

    if response.status_code != 200:
        raise Exception(f"PDF parsing upload failed with status {response.status_code}: {response.text}")

print("Parsing response received, proceeding to dataprep ingestion.")

# Step 2: Dataprep
payload = {
    'user': user,
    'collection_name': collection_name,
    'filename': "2305.15032v1-2-3.pdf",
}

response2 = requests.post(dataprep_ingest_url, data=payload)

if response2.status_code != 200:
    raise Exception(f"Data prep ingestion failed with status {response2.status_code}: {response2.text}")

print("Data prep ingestion completed successfully.")
