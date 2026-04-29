"""
capture.py - Screen capture module using mss for fast region capture
"""
import mss
import mss.tools
import numpy as np
from PIL import Image


class ScreenCapture:
    """Handles fast screen region capture using mss."""

    def __init__(self):
        self.sct = mss.mss()
        self.region = None  # {"top": y, "left": x, "width": w, "height": h}

    def set_region(self, x1: int, y1: int, x2: int, y2: int):
        """Set the screen region to capture."""
        self.region = {
            "top": min(y1, y2),
            "left": min(x1, x2),
            "width": abs(x2 - x1),
            "height": abs(y2 - y1),
        }

    def capture(self) -> Image.Image | None:
        """Capture current region and return as PIL Image."""
        if not self.region or self.region["width"] == 0 or self.region["height"] == 0:
            return None
        try:
            screenshot = self.sct.grab(self.region)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            return img
        except Exception as e:
            print(f"[Capture] Loi chup man hinh: {e}")
            return None

    def capture_as_numpy(self) -> np.ndarray | None:
        """Capture and return as numpy array (for EasyOCR)."""
        img = self.capture()
        if img is None:
            return None
        return np.array(img)

    def has_region(self) -> bool:
        return self.region is not None and self.region["width"] > 10 and self.region["height"] > 10
