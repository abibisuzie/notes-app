# Notes API

A tiny Python app (FastAPI + Postgres) for learning Docker and Kubernetes.
The app is done. Your job is everything around it.

## What it does

| Method | Path      | What it does                                   |
|--------|-----------|------------------------------------------------|
| GET    | `/`       | Says hello and shows which machine answered    |
| GET    | `/health` | Checks the app can reach the database          |
| POST   | `/notes`  | Adds a note: `{"text": "hello"}`               |
| GET    | `/notes`  | Lists all notes                                |

Interactive docs are at `http://localhost:8000/docs` once it's running.

## Configuration

One environment variable:

- `DATABASE_URL`, default `postgresql://notes:notes@localhost:5432/notes`

## Run it locally (before any containers)

You need Python 3.11+ and a Postgres database. The easiest Postgres is
Docker itself, which doubles as your first Phase 1 exercise:

```bash
docker run -d --name notes-db \
  -e POSTGRES_USER=notes -e POSTGRES_PASSWORD=notes -e POSTGRES_DB=notes \
  -p 5432:5432 postgres:16
```

Then start the app:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Try it:

```bash
curl -X POST localhost:8000/notes -H "Content-Type: application/json" -d '{"text":"my first note"}'
curl localhost:8000/notes
```

## Your tasks (this is the actual learning)

1. **Phase 2:** Write a `Dockerfile` for this app. Hint: start `FROM python:3.12-slim`,
   install `requirements.txt`, and run `uvicorn main:app --host 0.0.0.0 --port 8000`.
   Why `0.0.0.0` and not the default? Find out. It's a classic container gotcha.
2. **Phase 3:** Write a `compose.yaml` that runs this app and Postgres together.
   Hint: inside Compose, the database host is the *service name*, not `localhost`.
3. **Phase 4:** Deploy it to a `kind` cluster. Scale to 3 replicas and hit `/`
   several times. Watch `served_by` change.
4. **Phase 5:** Point a liveness and readiness probe at `/health`. Stop the
   database and see what Kubernetes does.

Things you'll hit on purpose along the way:
- The app crashes on startup if the database isn't ready yet. How do Compose
  (`depends_on` + healthcheck) and Kubernetes (restarts, probes) each handle that?
- The password is in `DATABASE_URL`. Where should it live in Compose? In Kubernetes?
