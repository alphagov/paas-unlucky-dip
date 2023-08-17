from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import crud
from app.config import Config
from app.s3 import S3Client
from app.templates import html_templates

from app.models import UUID4


router = APIRouter()


@router.get("/")
@router.get("/set/{incident_set_id}")
async def ui_wheel(
    request: Request,
    incident_set_id: str | None = None,
):
    title_suffix = f" ({incident_set_id})" if incident_set_id else ""
    if incident_set_id is None:
        incident_set_id = Config.default_id

    try:
        incident_set = crud.get_incident_set(S3Client, incident_set_id)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return html_templates.TemplateResponse(
        "wheel.html",
        {
            "request": request,
            "incident_set": incident_set,
            "title_suffix": title_suffix,
        },
    )


@router.get("/manage")
@router.get("/manage/list")
async def ui_manage_list(request: Request):
    context = {
        "request": request,
        "action": "list",
        "incident_sets": [],
    }
    if "user" in request.session.keys():
        context["incident_sets"] = crud.get_all_incident_sets(
            S3Client, request.session["user"]["login"]
        )
    return html_templates.TemplateResponse(
        "manage.html",
        context=context,
    )


@router.get("/manage/new")
async def ui_manage_new(request: Request):
    return html_templates.TemplateResponse(
        "manage.html",
        context={
            "request": request,
            "action": "new",
        },
    )


@router.get("/manage/edit/{incident_set_id}")
async def ui_manage_edit(request: Request, incident_set_id: UUID4):
    try:
        incident_set = crud.get_incident_set(S3Client, incident_set_id)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return html_templates.TemplateResponse(
        "manage.html",
        context={
            "request": request,
            "action": "edit",
            "incident_set": incident_set,
        },
    )


@router.get("/manage/delete/{incident_set_id}")
async def ui_manage_delete(request: Request, incident_set_id: UUID4):
    try:
        incident_set = crud.get_incident_set(S3Client, incident_set_id)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return html_templates.TemplateResponse(
        "manage.html",
        context={
            "request": request,
            "action": "delete",
            "incident_set": incident_set,
        },
    )


@router.get("/{page}")
@router.get("/{page}.html")
async def ui_page(request: Request, page: str):
    return html_templates.TemplateResponse(
        f"{page}.html",
        {
            "request": request,
        },
    )
