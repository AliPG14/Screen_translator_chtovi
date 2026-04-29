"""
main.py - Douyin Screen Translator
Entry point: orchestrates OCR, translation, overlay, and control panel
"""
import threading
import time
import sys
import os

# ── Force UTF-8 output on Windows ──────────────────────────────────────────
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from capture import ScreenCapture
from ocr import OCREngine
from translator import Translator
from overlay import TranslationOverlay
from selector import RegionSelector
from ui import ControlPanel


class DouyinTranslatorApp:
    """Main application controller."""

    def __init__(self):
        self.capture = ScreenCapture()
        self.translator = Translator(source="zh-CN", target="vi")
        self.overlay = TranslationOverlay()

        self._ocr: OCREngine | None = None
        self._ocr_ready = False
        self._running = False
        self._interval = 0.5
        self._last_text = ""
        self._worker_thread: threading.Thread | None = None
        self._overlay_thread: threading.Thread | None = None

        # Control panel (runs on main thread)
        self.panel = ControlPanel(
            on_select_region=self._select_region,
            on_start=self._start_translation,
            on_stop=self._stop_translation,
            on_toggle_overlay=self._toggle_overlay,
            on_interval_change=self._set_interval,
            on_quit=self._quit,
        )

    # ── Setup ────────────────────────────────────────────────────────────────

    def _load_ocr_async(self):
        """Load EasyOCR model in background so UI doesn't freeze."""
        try:
            self.panel.set_status("Đang tải mô hình OCR...", ready=False)
            self._ocr = OCREngine(use_gpu=False)
            self._ocr_ready = True
            self.panel.set_status("Sẵn sàng — Hãy chọn vùng", ready=True)
            print("[App] OCR da san sang!")
        except Exception as e:
            print(f"[App] Loi khi tai OCR: {e}")
            self.panel.set_status(f"Lỗi OCR: {e}", ready=False)

    # ── Region selection ─────────────────────────────────────────────────────

    def _select_region(self):
        """Open the region selector (runs on its own thread)."""
        def _run():
            selector = RegionSelector(self._on_region_selected)
            selector.start()
        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def _on_region_selected(self, region):
        self.capture.set_region(region.x1, region.y1, region.x2, region.y2)
        self.panel.set_region_info(region)
        self.panel.set_status("Vùng đã chọn — Nhấn Bắt Đầu", ready=True)
        print(f"[App] Vung da chon: {region.x1},{region.y1} -> {region.x2},{region.y2}")

    # ── Translation loop ─────────────────────────────────────────────────────

    def _start_translation(self):
        if not self._ocr_ready:
            self.panel.set_status("OCR chưa sẵn sàng, vui lòng chờ...", ready=False)
            return
        if not self.capture.has_region():
            self.panel.set_status("Chưa chọn vùng!", ready=False)
            return

        self._running = True
        self._last_text = ""
        self.overlay.show()
        self.overlay.set_status("▶ Đang dịch...")

        self._worker_thread = threading.Thread(target=self._translation_loop, daemon=True)
        self._worker_thread.start()
        self.panel.set_status("Đang dịch...", ready=True)

    def _stop_translation(self):
        self._running = False
        self.overlay.set_status("⏹ Đã dừng")
        self.panel.set_status("Đã dừng", ready=False)

    def _translation_loop(self):
        """Background thread: capture → OCR → translate → update overlay."""
        while self._running:
            start = time.time()
            try:
                img = self.capture.capture_as_numpy()
                if img is None:
                    time.sleep(0.5)
                    continue

                raw_text = self._ocr.extract_text(img, min_confidence=0.4)

                if not raw_text.strip():
                    self.overlay.set_status("🔍 Không tìm thấy chữ...", "#888888")
                    time.sleep(self._interval)
                    continue

                # Only translate if text changed
                if raw_text == self._last_text:
                    elapsed = time.time() - start
                    sleep_time = max(0, self._interval - elapsed)
                    time.sleep(sleep_time)
                    continue

                self._last_text = raw_text
                self.overlay.set_status("🌐 Đang dịch...", "#AAAAAA")

                translated = self.translator.translate(raw_text)
                ts = time.strftime("%H:%M:%S")
                self.overlay.update_text(
                    original=raw_text,
                    translation=translated,
                    status=f"✓ Cập nhật lúc {ts}",
                )

            except Exception as e:
                print(f"[Loop] Loi: {e}")
                self.overlay.set_status(f"❌ Lỗi: {str(e)[:40]}", "#FF5555")

            elapsed = time.time() - start
            sleep_time = max(0, self._interval - elapsed)
            time.sleep(sleep_time)

    # ── Controls ─────────────────────────────────────────────────────────────

    def _set_interval(self, value: float):
        self._interval = value

    def _toggle_overlay(self, visible: bool):
        if visible:
            self.overlay.show()
        else:
            self.overlay.hide()

    def _quit(self):
        self._running = False
        self.overlay.destroy()
        print("[App] Thoat.")

    # ── Entry ─────────────────────────────────────────────────────────────────

    def run(self):
        """Start the app: overlay on background thread, panel on main thread."""
        print("=" * 50)
        print("  Douyin Screen Translator")
        print("  github.com/antigravity-ai")
        print("=" * 50)

        # Start overlay on its own thread
        self._overlay_thread = threading.Thread(target=self.overlay.start, daemon=True)
        self._overlay_thread.start()
        time.sleep(0.3)  # Let overlay init

        # Load OCR in background
        ocr_thread = threading.Thread(target=self._load_ocr_async, daemon=True)
        ocr_thread.start()

        # Run control panel on MAIN thread (tkinter requirement)
        self.panel.run()


if __name__ == "__main__":
    app = DouyinTranslatorApp()
    app.run()
