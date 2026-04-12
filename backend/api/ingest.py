from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz
from typing import Any
import tempfile
import os

from . import shared

router = APIRouter()


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> Any:
    content = await file.read()
    print("content: {content}")
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    text = ""
    if ext in ["txt", "md"]:
        text = content.decode("utf-8")
    elif ext == "pdf":
        doc = fitz.open(stream=content, filetype="pdf")
        text = "\n".join(page.get_text("text") for page in doc)
        doc.close()
    elif ext in ["jpg", "jpeg", "png"]:
        print("from image reading block..")
        import importlib

        # Resolve OCR helper robustly across different run contexts
        ocr_candidates = ["utils.ocr_image_to_text"]

        ocr_image_to_text = None
        for cand in ocr_candidates:
            try:
                if cand.startswith("."):
                    mod = importlib.import_module(cand, package=__package__)
                else:
                    mod = importlib.import_module(cand)
                ocr_image_to_text = getattr(mod, "ocr_image_to_text")
                break
            except Exception:
                continue

        if ocr_image_to_text is None:
            raise HTTPException(500, "OCR helper module not found")

        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = ocr_image_to_text(tmp_path)
        print("generated text: {text}")
        print(text)
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
    else:
        raise HTTPException(400, "Unsupported file type")

    if not text.strip():
        raise HTTPException(400, "No text extracted")

    # Add date metadata
    from datetime import datetime

    current_date = datetime.now().isoformat()

    docs = shared.text_splitter.create_documents(
        [text],
        metadatas=[
            {
                "source": filename,
                "file_type": ext,
                "date_added": current_date,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        ],
    )

    shared.vectorstore.add_documents(docs)
    return {"status": "added", "chunks": len(docs), "source": filename}
