# ML Integration — FastAPI + React (Containerized)

This package contains a full project (backend + frontend) integrated with Mercado Libre API,
ready to run via Docker Compose (Postgres + pgAdmin included).

## Quick start

1. Copy `.env.example` to `backend/.env` and fill the required variables (ML credentials and SECRET_KEY).
2. Build and run:
   ```bash
   docker-compose up --build
   ```
3. Backend: http://localhost:8000
   - Open API docs: http://localhost:8000/docs
4. Frontend: http://localhost:3000
5. pgAdmin: http://localhost:8080 (login admin@admin.com / admin)

## Tests

To run backend tests locally (without Docker):
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Notes

- You must register your app at Mercado Libre developers, set Redirect URI to:
  `http://localhost:8000/api/oauth/callback`
- Generate a strong SECRET_KEY for production and store secrets securely.
