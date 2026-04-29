"""
ui.py - Control panel: the small always-on-top toolbar for controlling the app
"""
import tkinter as tk
from tkinter import ttk
import threading


class ControlPanel:
    """
    A compact floating control panel with:
    - [Chọn vùng] button
    - [Bắt đầu / Dừng] toggle
    - [Ẩn/Hiện Overlay] toggle
    - Status indicator
    - Interval slider
    """

    BG = "#111111"
    ACCENT = "#00FFAA"
    BTN_BG = "#1E1E1E"
    BTN_FG = "#EEEEEE"
    BTN_ACTIVE = "#00FFAA"
    TEXT_FG = "#AAAAAA"

    def __init__(
        self,
        on_select_region,
        on_start,
        on_stop,
        on_toggle_overlay,
        on_interval_change,
        on_quit,
    ):
        self.on_select_region = on_select_region
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_toggle_overlay = on_toggle_overlay
        self.on_interval_change = on_interval_change
        self.on_quit = on_quit

        self.root = None
        self._running = False
        self._overlay_visible = True

    def _make_btn(self, parent, text, command, width=12, color=None):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.BTN_BG,
            fg=color or self.BTN_FG,
            activebackground=self.ACCENT,
            activeforeground="#000000",
            relief="flat",
            bd=0,
            padx=8,
            pady=3,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            width=width,
        )
        btn.bind("<Enter>", lambda e: btn.config(bg="#2A2A2A"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.BTN_BG))
        return btn

    def build(self):
        self.root = tk.Tk()
        self.root.title("Douyin Dịch")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.96)
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        # Position: top-right corner
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"300x220+{sw - 320}+20")

        # ── Header ──────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg="#0A0A0A", pady=6)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🎵  Douyin Translator",
            fg=self.ACCENT,
            bg="#0A0A0A",
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.LEFT, padx=12)

        # Drag support
        header.bind("<ButtonPress-1>", self._start_drag)
        header.bind("<B1-Motion>", self._do_drag)

        # Close
        close = tk.Label(header, text="✕", fg="#444", bg="#0A0A0A",
                         font=("Segoe UI", 11, "bold"), cursor="hand2")
        close.pack(side=tk.RIGHT, padx=10)
        close.bind("<Button-1>", lambda e: self._quit())
        close.bind("<Enter>", lambda e: close.config(fg="#FF5555"))
        close.bind("<Leave>", lambda e: close.config(fg="#444"))

        # ── Body ─────────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=self.BG, padx=12, pady=8)
        body.pack(fill=tk.BOTH, expand=True)

        # Status
        self._status_dot = tk.Label(body, text="●", fg="#FF4444", bg=self.BG,
                                    font=("Segoe UI", 10))
        self._status_dot.grid(row=0, column=0, sticky="w")
        self._status_label = tk.Label(body, text="Chưa chọn vùng", fg=self.TEXT_FG,
                                      bg=self.BG, font=("Segoe UI", 9))
        self._status_label.grid(row=0, column=1, columnspan=2, sticky="w", padx=4)

        # Select region button
        self._sel_btn = self._make_btn(body, "🖱 Chọn Vùng", self._do_select, width=14)
        self._sel_btn.grid(row=1, column=0, columnspan=2, pady=(8, 4), sticky="ew")

        # Start / Stop button
        self._run_btn = self._make_btn(body, "▶ Bắt Đầu", self._toggle_run,
                                       width=13, color=self.ACCENT)
        self._run_btn.grid(row=2, column=0, pady=3, sticky="ew", padx=(0, 3))

        # Overlay toggle
        self._ovl_btn = self._make_btn(body, "👁 Ẩn Overlay", self._toggle_overlay, width=13)
        self._ovl_btn.grid(row=2, column=1, pady=3, sticky="ew", padx=(3, 0))

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        # ── Interval slider ──────────────────────────────────────────────
        tk.Label(body, text="Tần suất dịch (giây):", fg=self.TEXT_FG,
                 bg=self.BG, font=("Segoe UI", 8)).grid(row=3, column=0,
                 columnspan=2, sticky="w", pady=(8, 0))

        self._interval_var = tk.DoubleVar(value=1.5)
        slider = tk.Scale(
            body,
            from_=0.5, to=5.0, resolution=0.5,
            orient=tk.HORIZONTAL,
            variable=self._interval_var,
            bg=self.BG, fg=self.TEXT_FG,
            troughcolor="#1E1E1E",
            activebackground=self.ACCENT,
            highlightthickness=0,
            command=lambda v: self.on_interval_change(float(v)),
            length=255,
        )
        slider.grid(row=4, column=0, columnspan=2, sticky="ew")

        # ── Region info ──────────────────────────────────────────────────
        self._region_info = tk.Label(
            body, text="Vùng: chưa chọn", fg="#444444",
            bg=self.BG, font=("Segoe UI", 8)
        )
        self._region_info.grid(row=5, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self._drag_x = 0
        self._drag_y = 0

    def set_status(self, text: str, ready: bool = False):
        if not self.root:
            return
        color = self.ACCENT if ready else "#FF4444"
        self.root.after(0, lambda: (
            self._status_dot.config(fg=color),
            self._status_label.config(text=text),
        ))

    def set_region_info(self, region):
        if not self.root:
            return
        info = f"Vùng: {region.width}×{region.height}px  @({region.x1},{region.y1})"
        self.root.after(0, lambda: self._region_info.config(text=info))

    def _do_select(self):
        if self._running:
            self._toggle_run()  # Stop first
        self.root.withdraw()
        # Small delay so window hides before selector appears
        self.root.after(150, lambda: (
            self.on_select_region(),
            self.root.after(500, self.root.deiconify),
        ))

    def _toggle_run(self):
        if self._running:
            self._running = False
            self._run_btn.config(text="▶ Bắt Đầu", fg=self.ACCENT)
            self.on_stop()
        else:
            self._running = True
            self._run_btn.config(text="⏹ Dừng", fg="#FF7777")
            self.on_start()

    def _toggle_overlay(self):
        self._overlay_visible = not self._overlay_visible
        if self._overlay_visible:
            self._ovl_btn.config(text="👁 Ẩn Overlay")
        else:
            self._ovl_btn.config(text="🙈 Hiện Overlay")
        self.on_toggle_overlay(self._overlay_visible)

    def _quit(self):
        self._running = False
        self.on_quit()
        if self.root:
            self.root.destroy()

    def _start_drag(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _do_drag(self, event):
        nx = event.x_root - self._drag_x
        ny = event.y_root - self._drag_y
        self.root.geometry(f"+{nx}+{ny}")

    def run(self):
        """Start the tkinter event loop (must be called from main thread)."""
        self.build()
        self.root.mainloop()
