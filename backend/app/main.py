from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.initDb import initDb
from app.api.controller.router import apiRouter

app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apiRouter)

@app.on_event("startup")
def startup():
    initDb()

@app.get("/health")
def health():
    return {"status": "ok", "version": settings.app_version}
