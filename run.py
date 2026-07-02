import subprocess
import time
import sys

print("==================================================")
print("🚀 STARTING AI CRYPTO INVESTMENT INTELLIGENCE SYSTEM")
print("==================================================")

# 1. Khởi chạy FastAPI Backend (Cổng 8000)
print("\n[1/2] Kích hoạt FastAPI AI Engine...")
api_process = subprocess.Popen(
    [
        sys.executable, "-m", "uvicorn",
        "api:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload" # Tự động cập nhật code khi bạn chỉnh sửa backend
    ]
)

# Chờ 3 giây để FastAPI khởi tạo hoàn toàn và tải mô hình NLP FinBERT vào bộ nhớ
time.sleep(3)

# 2. Khởi chạy Giao diện Streamlit UI (Cổng 8501)
print("\n[2/2] Kích hoạt Streamlit Giao diện Người dùng...")
ui_process = subprocess.Popen(
    [
        sys.executable, "-m", "streamlit",
        "run", "app.py"
    ]
)

print("\n Hệ thống đã sẵn sàng! Bấm Ctrl+C trong Terminal này để tắt toàn bộ dịch vụ.")
print("==================================================")

try:
    # Giữ luồng chính luôn chạy để giám sát cả 2 tiến trình
    api_process.wait()
    ui_process.wait()
except KeyboardInterrupt:
    print("\n🛑 Đang dừng toàn bộ hệ thống hệ thống...")
    api_process.terminate()
    ui_process.terminate()
    print(" Hệ thống đã tắt an toàn.")