from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
import easyocr

# Reuse config
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "second_brain_v1"
EMBEDDING_MODEL = "all-minilm"
LLM_MODEL = "llama3.2:3b"

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)
llm = ChatOllama(model=LLM_MODEL, temperature=0.3)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
ocr_reader = easyocr.Reader(["en"], gpu=False)
