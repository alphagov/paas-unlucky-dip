#!/usr/bin/env python3
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import crud
from app.auth import OAuthConfig
from app.index import Index as _
from app.routers import auth as auth_router
from app.routers import incident_sets, specific_files, ui
from app.s3 import S3Client


app = FastAPI(title="main app")


@app.on_event("startup")
async def startup_event():
    crud.init_default_incident_set(
        S3Client,
        Path.cwd() / "default_incidents.json",
    )


app.add_middleware(SessionMiddleware, secret_key=OAuthConfig.SECRET_KEY)
app.mount("/static", StaticFiles(directory="ui/static", html=True), name="static")
app.include_router(auth_router.router, prefix="/auth")
app.include_router(incident_sets.router, prefix="/api/v1")
app.include_router(specific_files.router, prefix="")
app.include_router(ui.router, prefix="")
