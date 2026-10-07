"""Notes API: a tiny FastAPI app backed by Postgres.

All configuration comes from environment variables, which is exactly
what Docker and Kubernetes expect. Nothing is hard-coded.
"""
import os
import socket
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://notes:notes@localhost:5432/notes"
)

def get_conn():
    return psycopg.connect(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the app starts: make sure the table exists
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now()
            )
            """
        )
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


class NoteIn(BaseModel):
    text: str


@app.get("/")
def root():
    # The hostname tells you WHICH container/pod answered.
    # Useful later when you scale to 3 replicas in Kubernetes.
    return {"app": "notes", "served_by": socket.gethostname()}


@app.get("/health")
def health():
    # Used later for Kubernetes liveness/readiness probes.
    with get_conn() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}


@app.post("/notes", status_code=201)
def add_note(note: NoteIn):
    with get_conn() as conn:
        row = conn.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id, text, created_at",
            (note.text,),
        ).fetchone()
    return {"id": row[0], "text": row[1], "created_at": row[2]}


@app.get("/notes")
def list_notes():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC"
        ).fetchall()
    return [{"id": r[0], "text": r[1], "created_at": r[2]} for r in rows]