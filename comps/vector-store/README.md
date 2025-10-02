# Qdrant Vector Store with LangChain

A complete example demonstrating how to use **Qdrant** as a vector store with **LangChain** and **HuggingFace embeddings**. This implementation provides a simple yet powerful way to perform semantic similarity searches on your text data.

## Overview

This project includes a Python script that:
- Connects to a local Qdrant instance
- Creates and manages vector collections
- Generates embeddings using HuggingFace models
- Performs similarity searches on stored documents

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**
- **Docker** (for running Qdrant locally)
- **uv** (Python package manager)

## Quick Start

### Step 1: Start Qdrant with Docker

Launch a local Qdrant instance using Docker:

```bash
# Pull and run Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

For a detached mode (runs in background):

```bash
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant
```

**Port Configuration:**
- `6333` - HTTP API endpoint
- `6334` - gRPC API endpoint

**Verify Installation:**

```bash
curl http://localhost:6333/collections
```

You should receive an empty collection list `{"result": {"collections": []}}` if this is a fresh installation.

### Step 2: Set Up Python Environment

Create and activate a virtual environment (recommended):

```bash
# Create virtual environment
uv venv --python=3.12
# Activate the env
source .venv/bin/activate
```

Install required dependencies:

```bash
uv pip install -r requirements.txt
```

### Step 3: Run the Example Script

Execute the main script:

```bash
python3 main.py
```


## How It Works

The script performs the following operations:

1. **Connects** to the local Qdrant instance at `http://localhost:6333`
2. **Creates** a collection named `test_vectors` (if it doesn't exist)
3. **Initializes** embeddings using the `sentence-transformers/all-MiniLM-L6-v2` model
4. **Adds** sample texts to the vector store
5. **Executes** a similarity search query

### Expected Output

```
Collection 'test_vectors' created!
Added 4 texts to the vector store.

Top results for query: Test embeddings
1: I am testing embeddings
2: This is a test document
```

## Customization

### Changing the Embedding Model

The default model uses **384-dimensional vectors**. To use a different model:

1. Update the model name in the script
2. Adjust the collection vector size accordingly
3. Ensure the model is compatible with `sentence-transformers`

### Adding Your Own Data

Modify the `texts` variable in `main.py`:

```python
texts = [
    "Your first document",
    "Your second document",
    "Your third document"
]
```

## Docker Management

### Stop Qdrant Container

```bash
docker stop qdrant
```

### Restart Qdrant Container

```bash
docker start qdrant
```

### Remove Qdrant Container

```bash
docker rm -f qdrant
```

### View Qdrant Logs

```bash
docker logs qdrant
```

## Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [HuggingFace Sentence Transformers](https://huggingface.co/sentence-transformers)

## Troubleshooting

**Issue:** Connection refused to Qdrant
- **Solution:** Ensure Qdrant container is running with `docker ps`

**Issue:** Module import errors
- **Solution:** Verify all dependencies are installed with `pip list`

**Issue:** Out of memory errors
- **Solution:** Consider using a smaller embedding model or increasing Docker memory limits

## License

This project is provided as-is for educational and development purposes.

---

**Happy Vector Searching! 🔍**