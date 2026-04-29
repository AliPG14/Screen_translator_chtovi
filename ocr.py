"""
ocr.py - OCR engine using EasyOCR for Chinese text recognition
"""
import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging

# Suppress noisy EasyOCR / torch logs during warmup
logging.getLogger("easyocr").setLevel(logging.ERROR)


class OCREngine:
    """OCR engine for reading Simplified Chinese text from images."""

    # Language codes: ch_sim = Simplified Chinese, en = English
    LANGUAGES = ["ch_sim", "en"]

    def __init__(self, use_gpu: bool = False):
        print("[OCR] Dang khoi dong EasyOCR... (co the mat vai giay)")
        self.reader = easyocr.Reader(self.LANGUAGES, gpu=use_gpu)
        print("[OCR] Reader da tao. Bat dau warmup cac model...")
        self._warmup()
        print("[OCR] EasyOCR san sang! (tat ca model da load xong)")

    def _warmup(self):
        """Force-load all language models by running a silent dummy inference.

        EasyOCR lazy-loads recognition models on first readtext() call.
        Without this, the Chinese (ch_sim) model loads during the first real
        capture, causing a ~3-minute freeze that looks like "no text found".
        """
        try:
            # Tiny white image — OCR will find nothing, but all models load
            dummy = np.full((64, 256, 3), 255, dtype=np.uint8)
            self.reader.readtext(dummy, detail=0)
            print("[OCR] Warmup hoan thanh.")
        except Exception as e:
            print(f"[OCR] Warmup that bai (khong nghiem trong): {e}")

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Enhance image for better OCR accuracy."""
        pil_img = Image.fromarray(image)
        # Increase contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.5)
        # Sharpen
        pil_img = pil_img.filter(ImageFilter.SHARPEN)
        return np.array(pil_img)

    def extract_text(self, image: np.ndarray, min_confidence: float = 0.3) -> str:
        """Extract text from image using EasyOCR."""
        if image is None or image.size == 0:
            return ""
        try:
            processed = self.preprocess(image)
            results = self.reader.readtext(processed, detail=1, paragraph=False)

            # Filter by confidence and sort by vertical position (top to bottom)
            valid = [
                (bbox, text, conf)
                for bbox, text, conf in results
                if conf >= min_confidence and text.strip()
            ]
            # Sort by y-position of top-left corner
            valid.sort(key=lambda r: r[0][0][1])

            lines = self._group_into_lines(valid)
            return "\n".join(lines)

        except Exception as e:
            print(f"[OCR] Loi: {e}")
            return ""

    def _group_into_lines(self, results, y_threshold: int = 20) -> list[str]:
        """Group text boxes into lines based on y-coordinate proximity."""
        if not results:
            return []

        lines = []
        current_line = []
        current_y = results[0][0][0][1]  # y of first bbox top-left

        for bbox, text, conf in results:
            y = bbox[0][1]
            if abs(y - current_y) > y_threshold:
                if current_line:
                    # Sort by x and join
                    current_line.sort(key=lambda x: x[0])
                    lines.append(" ".join(t for _, t in current_line))
                current_line = []
                current_y = y
            current_line.append((bbox[0][0], text))

        if current_line:
            current_line.sort(key=lambda x: x[0])
            lines.append(" ".join(t for _, t in current_line))

        return lines
