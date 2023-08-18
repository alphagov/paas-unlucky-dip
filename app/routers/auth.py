from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from app.auth import OAuthConfig
from app.models import GithubUser

router = APIRouter()


@router.get("/login")
async def auth_login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    request.session["pre_login_url"] = request.headers.get("referer", "/")
    return await OAuthConfig.client.authorize_redirect(request, redirect_uri)


@router.get("/logout")
async def auth_logout(request: Request):
    request.session.clear()
    return RedirectResponse(request.headers.get("referer", "/"))


@router.get("/callback")
async def auth_callback(request: Request):
    try:
        token = await OAuthConfig.client.authorize_access_token(request)
    except OAuthError:
        return Response("Authentication failed", status_code=401)
    user_data = await OAuthConfig.client.userinfo(token=token)
    user_object = GithubUser(**user_data)
    if not await OAuthConfig.user_is_org_member(token=token, user=user_object):
        request.session.clear()
        return Response("User is not an org member", status_code=401)
    request.session["user"] = user_object.model_dump(mode="json")

    return RedirectResponse(request.session.pop("pre_login_url"))
