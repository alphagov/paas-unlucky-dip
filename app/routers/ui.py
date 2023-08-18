from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.status import HTTP_307_TEMPORARY_REDIRECT

from app import crud
from app.auth import RequestWithUser, verify_auth
from app.config import Config
from app.models import UUID4
from app.s3 import S3Client
from app.templates import html_templates


async def verify_user_ui(request: RequestWithUser):
    if not await verify_auth(request):
        raise HTTPException(
            status_code=HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": str(request.url_for("ui_manage_home"))},
        )
    return True


router = APIRouter()


@router.get("/")
@router.get("/set/{incident_set_id}")
async def ui_wheel(
    request: Request,
    incident_set_id: str | None = None,
):
    default_wheel = incident_set_id is None

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
            "title_suffix": "" if default_wheel else f" ({incident_set.display_name})",
            "subtitle": None
            if (default_wheel or incident_set.name is None)
            else incident_set.name,
        },
    )


@router.get("/manage")
async def ui_manage_home(
    request: RequestWithUser,
):
    return html_templates.TemplateResponse(
        "manage.html",
        context={
            "request": request,
            "action": "home",
        },
    )


@router.get("/manage/list", dependencies=[Depends(verify_user_ui)])
async def ui_manage_list(
    request: RequestWithUser,
):
    return html_templates.TemplateResponse(
        "manage.html",
        context={
            "request": request,
            "action": "list",
            "incident_sets": crud.get_all_incident_sets(
                S3Client, request.state.user.login
            ),
        },
    )


@router.get("/manage/new")
async def ui_manage_new(request: RequestWithUser):
    return html_templates.TemplateResponse(
        "manage.html",
        context={
            "request": request,
            "action": "new",
        },
    )


@router.get("/manage/edit/{incident_set_id}")
async def ui_manage_edit(
    request: RequestWithUser,
    incident_set_id: UUID4,
):
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
async def ui_manage_delete(request: RequestWithUser, incident_set_id: UUID4):
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
