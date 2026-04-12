import cv2
import easyocr
import re
from pathlib import Path
from difflib import get_close_matches

# Initialize once
ocr_reader = easyocr.Reader(["en"], gpu=False)


# -----------------------------
# 1. Score OCR output quality
# -----------------------------
def score_result(results):
    total_conf = 0
    total_len = 0

    for (_, text, conf) in results:
        total_conf += conf * len(text)
        total_len += len(text)

    return total_conf / (total_len + 1e-6)


# -----------------------------
# 2. Orientation Fix
# -----------------------------
def fix_orientation(img):
    rotations = [
        img,
        cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(img, cv2.ROTATE_180),
        cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
    ]

    best_img = img
    best_score = -1

    for r in rotations:
        results = ocr_reader.readtext(r, detail=1)
        score = score_result(results)

        if score > best_score:
            best_score = score
            best_img = r

    return best_img


# -----------------------------
# 3. Safe preprocessing
# -----------------------------
def preprocess_variants(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    variants = []

    # Keep original (important)
    variants.append(img)

    # Grayscale
    variants.append(gray)

    # Mild contrast
    contrast = cv2.convertScaleAbs(gray, alpha=1.1, beta=0)
    variants.append(contrast)

    return variants


# -----------------------------
# 4. Normalize repeated chars
# -----------------------------
def normalize_repeated_chars(text):
    return re.sub(r'(.)\1{2,}', r'\1\1', text)


# -----------------------------
# 5. Context-aware number normalization
# -----------------------------
def normalize_numbers(text):
    # Fix decimal issues
    text = re.sub(r'(\d)[,](\d)', r'\1.\2', text)
    text = re.sub(r'(\d)\s+(\d{2})\b', r'\1.\2', text)
    text = re.sub(r'(\d)\.0u', r'\1.00', text)

    # Replace O → 0 only in numeric context
    text = re.sub(r'(?<=\d)[Oo](?=\d)', '0', text)
    text = re.sub(r'(?<=\d)[Oo]\b', '0', text)

    return text


# -----------------------------
# 6. Generic vocabulary (not hardcoded to invoice)
# -----------------------------
COMMON_WORDS = [
    "total", "amount", "invoice", "date", "customer",
    "mobile", "discount", "gst", "payment", "type",
    "item", "name", "qty", "rate", "gross"
]


# -----------------------------
# 7. Fuzzy word correction
# -----------------------------
def correct_word(word):
    original = word
    word_lower = word.lower()

    # Skip words with numbers (avoid breaking values)
    if any(c.isdigit() for c in word):
        return word

    matches = get_close_matches(word_lower, COMMON_WORDS, n=1, cutoff=0.6)

    if matches:
        corrected = matches[0]
        return corrected.upper() if original.isupper() else corrected

    return word


def correct_line(text):
    words = text.split()
    corrected = [correct_word(w) for w in words]
    return " ".join(corrected)


# -----------------------------
# 8. Filter garbage text
# -----------------------------
def is_valid_text(text, conf):
    if conf < 0.2:
        return False

    # Remove lines like "2 2 1 1 1"
    digits = sum(c.isdigit() for c in text)
    if len(text) > 4 and digits / len(text) > 0.8:
        return False

    return True


# -----------------------------
# 9. Group lines
# -----------------------------
def group_lines(results):
    results = sorted(
        results,
        key=lambda x: (
            min(p[1] for p in x[0]),
            min(p[0] for p in x[0])
        )
    )

    lines = []
    current_line = []
    last_y = None

    for (bbox, text, conf) in results:
        if not text.strip():
            continue

        if not is_valid_text(text, conf):
            continue

        y_center = sum(p[1] for p in bbox) / 4
        height = max(p[1] for p in bbox) - min(p[1] for p in bbox)

        if last_y is None or abs(y_center - last_y) < height * 0.7:
            current_line.append((bbox, text))
        else:
            current_line = sorted(
                current_line,
                key=lambda x: min(p[0] for p in x[0])
            )

            line_text = " ".join(t for _, t in current_line)

            # Apply corrections in right order
            line_text = normalize_repeated_chars(line_text)
            line_text = normalize_numbers(line_text)
            line_text = correct_line(line_text)

            lines.append(line_text)
            current_line = [(bbox, text)]

        last_y = y_center

    if current_line:
        current_line = sorted(
            current_line,
            key=lambda x: min(p[0] for p in x[0])
        )

        line_text = " ".join(t for _, t in current_line)

        line_text = normalize_repeated_chars(line_text)
        line_text = normalize_numbers(line_text)
        line_text = correct_line(line_text)

        lines.append(line_text)

    return lines


# -----------------------------
# 10. MAIN FUNCTION
# -----------------------------
def ocr_image_to_text(file_path: Path):
    try:
        print("Running OCR...")

        img = cv2.imread(str(file_path))
        if img is None:
            return "Failed to read image"

        # Light upscale
        img = cv2.resize(img, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_CUBIC)

        # Fix orientation
        img = fix_orientation(img)

        # Try multiple variants
        variants = preprocess_variants(img)

        best_results = None
        best_score = -1

        for v in variants:
            results = ocr_reader.readtext(v, detail=1)
            score = score_result(results)

            if score > best_score:
                best_score = score
                best_results = results

        # Group lines
        lines = group_lines(best_results)

        formatted_text = "\n".join(lines)

        print("\n===== STRUCTURED OUTPUT =====\n")
        print(formatted_text)

        return formatted_text

    except Exception as e:
        print(f"OCR error: {e}")
        return "Failed to extract text"
