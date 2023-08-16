#!/usr/bin/env python3
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.defaults import DEFAULT_INCIDENT_SET_ID

from app import crud
from app.s3 import S3Client
from app.routers import ui, incident_sets, specific_files

crud.init_default_incident_set(
    S3Client,
    Path.cwd() / "default_incidents.json",
    incident_set_id=DEFAULT_INCIDENT_SET_ID,
)

app = FastAPI(title="main app")
app.mount("/static", StaticFiles(directory="ui/static", html=True), name="static")
app.include_router(incident_sets.router, prefix="/api/v1")
app.include_router(specific_files.router, prefix="")
app.include_router(ui.router, prefix="")
