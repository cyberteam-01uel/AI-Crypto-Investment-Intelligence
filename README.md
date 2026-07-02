# 🦅 AI Crypto Investment Intelligence Hub

Hệ thống phân tích, nghiên cứu và giám sát thị trường Crypto thông minh, được xây dựng dựa trên kiến trúc chia tách giữa giao diện tương tác và lõi xử lý API định lượng.

---

## 📂 Cấu Trúc Thành Phần Hệ Thống

Dưới đây là sơ đồ tổ chức thư mục của dự án:

* **`app.py`** — 🖥️ **Streamlit Main Hub**: Giao diện người dùng chính. Quản lý toàn bộ trải nghiệm tương tác trực quan, Chatbot KYC và render Dashboard đồ thị.
* **`api.py` / `run.py`** — ⚙️ **Backend Entrypoint**: Cổng khởi chạy máy chủ API (FastAPI) để điều phối dữ liệu nghiên cứu.
* **`profiling/`** — 👤 **User Profile Module**: 
    * `routers_pr.py` — Endpoint tiếp nhận dữ liệu phân tích hành vi và hồ sơ rủi ro của nhà đầu tư.
* **`research/`** — 📊 **Quantitative Core**:
    * `core_analysis.py` — Lõi tính toán điểm số kỹ thuật, đánh giá phân bổ danh mục và quản trị rủi ro.
    * `routers_re.py` — Endpoint xử lý và trả về ma trận dữ liệu tích hợp của các tài sản mục tiêu.

---

## 🛠️ Công Nghệ Sử Dụng

* **Frontend:** Streamlit, Plotly
* **Backend:** FastAPI (Python 3.11+)
* **Môi trường:** Docker, Virtualenv (`.venv`)