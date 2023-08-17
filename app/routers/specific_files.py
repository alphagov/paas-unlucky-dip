from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_308_PERMANENT_REDIRECT

from app.templates import misc_templates, js_templates

from app.config import Config

router = APIRouter()


@router.get("/site.webmanifest")
async def specific_webmanifest(request: Request):
    return misc_templates.TemplateResponse(
        "site.webmanifest",
        {
            "request": request,
        },
        media_type="application/manifest+json",
    )


@router.get("/favicon.ico")
async def specific_favicon(request: Request):
    return RedirectResponse(
        url=request.app.url_path_for("static", path="img/favicon.ico"),
        status_code=HTTP_308_PERMANENT_REDIRECT,
    )


@router.get("/js/wheel.js")
async def specific_wheel_js(request: Request, q: str = Config.default_id):
    if not q or q == "":
        q = Config.default_id
    return js_templates.TemplateResponse(
        "wheel.js",
        {
            "request": request,
            "incident_set_id": q,
        },
        media_type="application/javascript",
    )
