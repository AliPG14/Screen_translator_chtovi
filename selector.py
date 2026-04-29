"""
selector.py - Region selector: lets the user drag to pick a screen region
"""
import tkinter as tk
from dataclasses import dataclass


@dataclass
class Region:
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self):
        return abs(self.x2 - self.x1)

    @property
    def height(self):
        return abs(self.y2 - self.y1)

    @property
    def is_valid(self):
        return self.width > 10 and self.height > 10


class RegionSelector:
    """Full-screen transparent overlay for dragging to select a region."""

    def __init__(self, on_select_callback):
        self.callback = on_select_callback
        self._start_x = 0
        self._start_y = 0
        self._rect = None
        self.root = None
        self.canvas = None

    def start(self):
        """Open the selector window."""
        self.root = tk.Tk()
        self.root.title("Chon vung can dich")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="navy")
        self.root.config(cursor="crosshair")

        self.canvas = tk.Canvas(
            self.root,
            bg="navy",
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Instruction label
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            40,
            text="🖱️  Kéo chuột để chọn vùng cần dịch  •  Nhấn ESC để hủy",
            fill="white",
            font=("Segoe UI", 18, "bold"),
        )

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Escape>", lambda e: self._cancel())

        self.root.mainloop()

    def _on_press(self, event):
        self._start_x = event.x_root
        self._start_y = event.y_root
        if self._rect:
            self.canvas.delete(self._rect)

    def _on_drag(self, event):
        if self._rect:
            self.canvas.delete(self._rect)
        cx = event.x_root - self.root.winfo_rootx()
        cy = event.y_root - self.root.winfo_rooty()
        sx = self._start_x - self.root.winfo_rootx()
        sy = self._start_y - self.root.winfo_rooty()
        self._rect = self.canvas.create_rectangle(
            sx, sy, cx, cy,
            outline="#00FFAA",
            width=3,
            fill="#00FFAA",
            stipple="gray25",
        )

    def _on_release(self, event):
        region = Region(
            x1=min(self._start_x, event.x_root),
            y1=min(self._start_y, event.y_root),
            x2=max(self._start_x, event.x_root),
            y2=max(self._start_y, event.y_root),
        )
        self.root.destroy()
        self.root = None
        if region.is_valid:
            self.callback(region)

    def _cancel(self):
        if self.root:
            self.root.destroy()
            self.root = None
