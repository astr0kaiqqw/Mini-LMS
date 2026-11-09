from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import CORS_ORIGINS
from .db import engine
from .demo import COURSES

app = FastAPI(title="Mini LMS · Учебная мастерская", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_credentials=True,
    allow_headers=["*"],
)


@app.get("/health/live")
def live():
    return {"status": "ok", "mode": "learning"}


@app.get("/health/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT 1 FROM users JOIN courses ON false JOIN lesson_progress ON false JOIN grades ON false LIMIT 1"
                )
            )
        return {"status": "ok", "database": "reachable", "schema": "learning"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503, detail="БД или учебная схема недоступна"
        ) from None


@app.get("/api/demo/courses")
def courses():
    return {"mode": "demo", "persisted": False, "items": COURSES}


@app.get("/api/demo/courses/{course_id}")
def course(course_id: str):
    for item in COURSES:
        if item["id"] == course_id:
            return {"mode": "demo", "persisted": False, "item": item}
    raise HTTPException(status_code=404, detail="Курс не найден")


# TODO(W13, Ерасыл): QUIZ-01 — реализовать попытку теста, серверную проверку и интеграцию frontend.
# TODO(W14, Ерасыл): ASSIGN-01 — реализовать отправку задания и чтение оценки.

from .learning import router

app.include_router(router)
