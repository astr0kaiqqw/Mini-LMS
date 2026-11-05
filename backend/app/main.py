from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import CORS_ORIGINS
from .db import engine
from .demo import COURSES

app = FastAPI(title="Mini LMS · Учебная мастерская", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["GET"], allow_headers=["*"])

@app.get("/health/live")
def live():
    return {"status": "ok", "mode": "demo"}

@app.get("/health/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM users LIMIT 1"))
        return {"status": "ok", "database": "reachable", "schema": "initial"}
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="БД или начальная схема недоступна") from None

@app.get("/api/demo/courses")
def courses():
    return {"mode": "demo", "persisted": False, "items": COURSES}

@app.get("/api/demo/courses/{course_id}")
def course(course_id: str):
    for item in COURSES:
        if item["id"] == course_id:
            return {"mode": "demo", "persisted": False, "item": item}
    raise HTTPException(status_code=404, detail="Курс не найден")

# TODO(W12, Ануар): CONTENT-01 — заменить demo API чтением опубликованных курсов из PostgreSQL.
# TODO(W13, Ерасыл): QUIZ-01 — реализовать попытку теста, серверную проверку и интеграцию frontend.
# TODO(W14, Ануар): STAFF-01 — реализовать API материалов и проверку ролей на сервере.
# TODO(W14, Ерасыл): ASSIGN-01 — реализовать отправку задания и чтение оценки.
