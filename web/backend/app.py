# web/backend/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from web.backend.routes.predict import router as predict_router
from web.backend.routes.feedback import router as feedback_router
import mimetypes
mimetypes.add_type("application/javascript", ".js")

# 🔥 ROOT CHUẨN
BASE_DIR = Path(__file__).resolve().parents[1]

def create_app() -> FastAPI:
    app = FastAPI(
        title="Fake News Detection API",
        description="API nhận diện tin giả sử dụng AI",
        version="1.0.0"
    )

    # =========================
    # CORS
    # =========================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # =========================
    # STATIC FILES
    # =========================
    app.mount(
        "/static",
        StaticFiles(directory=BASE_DIR  / "static"),
        name="static"
    )

    app.mount(
        "/scripts",
        StaticFiles(directory=BASE_DIR / "scripts"),
        name="scripts"
    )

    # =========================
    # API ROUTES
    # =========================
    app.include_router(predict_router, prefix="/api", tags=["Prediction"])
    app.include_router(feedback_router, prefix="/api", tags=["Feedback"])

    # =========================
    # FRONTEND ENTRY
    # =========================
    @app.get("/", response_class=HTMLResponse)
    def index():
        html_path = BASE_DIR / "templates" / "index.html"
        return html_path.read_text(encoding="utf-8")

    @app.get("/result", response_class=HTMLResponse)
    def result():
        html_path = BASE_DIR   / "templates" / "result.html"
        return html_path.read_text(encoding="utf-8")

    return app


app = create_app()
