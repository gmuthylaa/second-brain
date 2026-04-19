from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
import easyocr

# Config
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "second_brain_v1"
EMBEDDING_MODEL = "all-minilm"
LLM_MODEL = "llama3.2:3b"

# Embeddings & LLM
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0.3,
    # Optional: add num_ctx if you need larger context
)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
ocr_reader = easyocr.Reader(["en"], gpu=False)

# Optional: Test embeddings once at startup (helps catch issues early)
try:
    _test = embeddings.embed_query("test")
    print("✅ Embeddings model loaded successfully")
except Exception as e:
    print(f"⚠️  Embedding test failed: {e}")