"""
overlay.py - Beautiful always-on-top translation overlay window
Uses tkinter with semi-transparent dark background and clean typography
"""
import tkinter as tk
from tkinter import font as tkfont
import threading


class TranslationOverlay:
    """
    A semi-transparent, always-on-top overlay window
    showing the translated text in a beautiful dark card style.
    """

    BG_COLOR = "#0D0D0D"
    ACCENT = "#00FFAA"
    TEXT_COLOR = "#F0F0F0"
    ORIG_COLOR = "#888888"
    HEADER_COLOR = "#00FFAA"
    WIDTH = 480
    MIN_HEIGHT = 80

    def __init__(self):
        self.root = None
        self._dragging = False
        self._drag_x = 0
        self._drag_y = 0
        self._current_text = ""
        self._current_orig = ""
        self._visible = False
        self._lock = threading.Lock()

    def _build(self):
        """Build the overlay window."""
        self.root = tk.Tk()
        self.root.overrideredirect(True)        # No title bar
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.92)    # Slight transparency
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)

        # Position: bottom center of screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - self.WIDTH) // 2
        y = sh - 220
        self.root.geometry(f"{self.WIDTH}x{self.MIN_HEIGHT}+{x}+{y}")

        # ── Outer frame with accent border ──────────────────────────────
        self._frame = tk.Frame(
            self.root,
            bg=self.BG_COLOR,
            highlightbackground=self.ACCENT,
            highlightthickness=2,
            padx=14,
            pady=10,
        )
        self._frame.pack(fill=tk.BOTH, expand=True)

        # ── Header bar ──────────────────────────────────────────────────
        header_frame = tk.Frame(self._frame, bg=self.BG_COLOR)
        header_frame.pack(fill=tk.X)

        self._header = tk.Label(
            header_frame,
            text="🎵",
            fg=self.HEADER_COLOR,
            bg=self.BG_COLOR,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self._header.pack(side=tk.LEFT)

        # Close button
        close_btn = tk.Label(
            header_frame,
            text="✕",
            fg="#555555",
            bg=self.BG_COLOR,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.hide())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg="#FF5555"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg="#555555"))

        # Divider
        tk.Frame(self._frame, bg=self.ACCENT, height=1).pack(fill=tk.X, pady=(4, 6))

        # ── Original text label ─────────────────────────────────────────
        self._orig_label = tk.Label(
            self._frame,
            text="",
            fg=self.ORIG_COLOR,
            bg=self.BG_COLOR,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
            wraplength=self.WIDTH - 40,
        )
        self._orig_label.pack(fill=tk.X)

        # ── Translation label ────────────────────────────────────────────
        self._trans_label = tk.Label(
            self._frame,
            text="",
            fg=self.TEXT_COLOR,
            bg=self.BG_COLOR,
            font=("Segoe UI", 14, "bold"),
            anchor="w",
            justify="left",
            wraplength=self.WIDTH - 40,
        )
        self._trans_label.pack(fill=tk.X, pady=(2, 0))

        # ── Status bar ──────────────────────────────────────────────────
        self._status = tk.Label(
            self._frame,
            text="⏳ Đang chờ...",
            fg="#555555",
            bg=self.BG_COLOR,
            font=("Segoe UI", 8),
            anchor="e",
        )
        self._status.pack(fill=tk.X, pady=(4, 0))

        # ── Drag-to-move binding ─────────────────────────────────────────
        for widget in [self._frame, self._header, self._orig_label]:
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)

        self.root.protocol("WM_DELETE_WINDOW", self.hide)

    def start(self):
        """Initialize and show overlay (call from main thread)."""
        self._build()
        self._visible = True
        self.root.mainloop()

    def update_text(self, original: str, translation: str, status: str = ""):
        """Thread-safe update of overlay text."""
        with self._lock:
            self._current_text = translation
            self._current_orig = original
        if self.root:
            self.root.after(0, self._refresh_ui, original, translation, status)

    def _refresh_ui(self, original: str, translation: str, status: str):
        if not self.root:
            return

        # Truncate long original text for display
        orig_display = original[:80] + "..." if len(original) > 80 else original
        orig_display = f"🇨🇳 {orig_display}" if orig_display else ""

        self._orig_label.config(text=orig_display)
        self._trans_label.config(text=f"🇻🇳 {translation}" if translation else "")
        self._status.config(text=status or "")

        # Auto-resize height
        self.root.update_idletasks()
        new_h = self._frame.winfo_reqheight() + 4
        new_h = max(new_h, self.MIN_HEIGHT)
        w = self.root.winfo_width()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.geometry(f"{w}x{new_h}+{x}+{y}")

    def set_status(self, text: str, color: str = "#555555"):
        if self.root:
            self.root.after(0, lambda: self._status.config(text=text, fg=color))

    def show(self):
        if self.root:
            self.root.after(0, self.root.deiconify)
            self._visible = True

    def hide(self):
        if self.root:
            self.root.after(0, self.root.withdraw)
            self._visible = False

    def destroy(self):
        if self.root:
            self.root.after(0, self.root.destroy)
            self.root = None

    def _start_drag(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _do_drag(self, event):
        nx = event.x_root - self._drag_x
        ny = event.y_root - self._drag_y
        self.root.geometry(f"+{nx}+{ny}")
