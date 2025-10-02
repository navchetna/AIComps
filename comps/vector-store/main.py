from langchain_community.vectorstores.qdrant import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings  # updated package
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

# --- Step 0: Connect and create collection ---
client = QdrantClient(host="localhost", port=6333)
collection_name = "test_vectors"

if collection_name not in [c.name for c in client.get_collections().collections]:
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"Collection '{collection_name}' created!")

# --- Step 1: Initialize embeddings ---
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- Step 2: Initialize LangChain Qdrant vector store ---
vectorstore = Qdrant(
    client=client,
    collection_name=collection_name,
    embeddings=embedding_model
)

# --- Step 3: Add texts ---
texts = [
    "Hello world",
    "This is a test document",
    "LangChain and Qdrant are awesome!",
    "I am testing embeddings"
]

vectorstore.add_texts(texts)
print(f"Added {len(texts)} texts to the vector store.")

# --- Step 4: Query ---
query = "Test embeddings"
results = vectorstore.similarity_search(query, k=2)

print("Top results for query:", query)
for i, res in enumerate(results, 1):
    print(f"{i}: {res.page_content}")
