from fastapi import APIRouter, HTTPException, Request


from app import crud
from app.defaults import DEFAULT_INCIDENT_SET_ID
from app.s3 import S3Client
from app.templates import html_templates

router = APIRouter()


@router.get("/")
@router.get("/set/{incident_set_id}")
async def ui_wheel(request: Request, incident_set_id: str = DEFAULT_INCIDENT_SET_ID):
    try:
        incident_set = crud.get_incident_set(S3Client, incident_set_id)
    except crud.ObjectNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Incident set not found") from exc
    return html_templates.TemplateResponse(
        "wheel.html",
        {
            "request": request,
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
