# Screen_translator_chtovi
A vibe code built in appication using python to translate chinese to vietnamese, in order for me to understand contents on douyin

# 🎵 Douyin Screen Translator

Phần mềm dịch chữ trực tiếp trên màn hình để xem Douyin — nhận diện chữ Trung Quốc bằng AI và dịch sang Tiếng Việt theo thời gian thực.

---

## ⚡ Cài Đặt

### Yêu cầu
- **Python 3.8+** — tải tại https://python.org
- Kết nối Internet (để dịch qua Google Translate)

### Cài thư viện
```bash
# Double-click file này, hoặc chạy trong terminal:
install.bat
```

Hoặc thủ công:
```bash
pip install mss easyocr deep-translator Pillow numpy pywin32
```

> ⚠️ Lần đầu chạy sẽ tải model EasyOCR (~300MB). Hãy kiên nhẫn!

---

## ▶️ Chạy Chương Trình

```bash
python main.py
```

---

## 🖱️ Hướng Dẫn Sử Dụng

1. **Mở Douyin** (trình duyệt hoặc giả lập Android)
2. **Chạy** `python main.py`
3. **Chờ** thanh điều khiển xuất hiện (góc trên phải)
4. Nhấn **"🖱 Chọn Vùng"** → kéo chuột chọn khu vực subtitle/chat
5. Nhấn **"▶ Bắt Đầu"** → overlay dịch sẽ hiện ở cuối màn hình
6. **Kéo** overlay để di chuyển vị trí tùy ý

---

## 🎛️ Tính Năng

| Tính năng | Mô tả |
|---|---|
| 🔍 OCR AI | EasyOCR nhận diện chữ Trung Giản Thể chính xác cao |
| 🌐 Dịch tức thì | Google Translate miễn phí, không cần API key |
| 📌 Always-on-top | Overlay luôn hiển thị trên Douyin |
| ⚡ Smart cache | Không dịch lại text giống nhau → nhanh hơn |
| 🎚️ Tuỳ chỉnh tần suất | Điều chỉnh 0.5s → 5s tùy tốc độ máy |
| 👁️ Ẩn/Hiện overlay | Bật tắt overlay khi không cần |
| 🖱️ Kéo được | Kéo cả overlay lẫn thanh điều khiển |

---

## 📁 Cấu Trúc

```
screen_translator/
├── main.py          # Entry point
├── capture.py       # Chụp màn hình (mss)
├── ocr.py           # Nhận diện chữ (EasyOCR)
├── translator.py    # Dịch thuật (Google Translate)
├── overlay.py       # Cửa sổ hiển thị dịch
├── selector.py      # Chọn vùng màn hình
├── ui.py            # Thanh điều khiển
├── requirements.txt
└── install.bat
```

---

## 🐛 Khắc Phục Lỗi

| Lỗi | Giải pháp |
|---|---|
| `ModuleNotFoundError` | Chạy lại `install.bat` |
| OCR không nhận chữ | Tăng độ sáng màn hình, chọn vùng rõ ràng hơn |
| Dịch bị lỗi | Kiểm tra kết nối Internet |
| Màn hình bị lag | Tăng interval lên 3-5 giây |
