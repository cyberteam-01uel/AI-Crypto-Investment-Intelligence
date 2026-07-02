from fastapi import FastAPI
from profiling.routers import router as profiling_router
from research.routers import router as research_router  # 🆕 Import thêm router của Chức năng 2

app = FastAPI(title="AI Engine")

# Đăng ký các phân hệ nghiệp vụ vào Backend
app.include_router(profiling_router)
app.include_router(research_router)  # 🆕 Kích hoạt cổng Chức năng 2

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "AI Engine"
    }