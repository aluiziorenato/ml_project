from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers import api_endpoints, api_tests, oauth, auth, proxy
from .config import settings

app = FastAPI(title="ML Integration Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(api_endpoints.router)
app.include_router(api_tests.router)
app.include_router(oauth.router)
app.include_router(proxy.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}
