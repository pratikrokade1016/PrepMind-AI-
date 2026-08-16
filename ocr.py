import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
import shutil

# -------------------------------
# 🔍 AUTO-DETECT TESSERACT PATH
# -------------------------------
def configure_tesseract():
    possible_paths = [
        "/opt/homebrew/bin/tesseract",                # Mac (M1/M2)
        "/usr/bin/tesseract",                         # Linux
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows
    ]

    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return

    # fallback: check if in PATH
    if shutil.which("tesseract"):
        pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")


configure_tesseract()


# -------------------------------
# 📷 OCR FUNCTION
# -------------------------------
def extract_text_from_image(file_path: str) -> str:
    try:
        img = cv2.imread(file_path)

        if img is None:
            print("❌ Image not loaded")
            return ""

        # Resize (improves accuracy)
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Noise removal
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Thresholding
        _, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # OCR config
        custom_config = r'--oem 3 --psm 6'

        text = pytesseract.image_to_string(thresh, config=custom_config)

        print("📄 Extracted Text:", text)

        return text.strip()

    except Exception as e:
        print("❌ OCR Error:", e)
        return ""