from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "second_brain_v1"
EMBEDDING_MODEL = "all-minilm"

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

print(f"Total documents in DB: {vectorstore._collection.count()}")

query = "back pain gym"
print(f"\nSearching for: '{query}'\n")

results = vectorstore.similarity_search(query, k=2)

for i, doc in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"Source: {doc.metadata.get('source', 'unknown')}")
    print(f"Content:\n{doc.page_content}\n")
    print("-" * 80)
