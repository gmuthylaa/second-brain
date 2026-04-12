from fastapi import APIRouter, UploadFile, File
import fitz
import tempfile
import os

from . import shared

router = APIRouter()


@router.post("/ingest/review")
async def ingest_review(file: UploadFile = File(...)):
    """Return OCR text for user review (especially for images)"""
    content = await file.read()
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    text = ""

    if ext in ["jpg", "jpeg", "png"]:
        print("📸 Running OCR for review...")
        import importlib

        ocr_candidates = [
            ".utils.ocr_image_to_text",
            "backend.utils.ocr_image_to_text",
            "utils.ocr_image_to_text",
            "ocr_image_to_text",
        ]

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
            return {"error": "OCR helper module not found"}

        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = ocr_image_to_text(tmp_path)

        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    elif ext in ["txt", "md"]:
        text = content.decode("utf-8")
    elif ext == "pdf":
        doc = fitz.open(stream=content, filetype="pdf")
        text = "\n".join(page.get_text("text") for page in doc)
        doc.close()
    else:
        return {"error": "Unsupported file type for review"}

    return {"filename": filename, "extracted_text": text, "file_type": ext}
