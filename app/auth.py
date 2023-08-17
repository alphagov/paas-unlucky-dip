import os


from authlib.integrations.starlette_client import OAuth as StarletteOAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App
from fastapi import HTTPException

from fastapi import Request


class OauthEnvarMissing(KeyError):
    def __init__(self, *args):
        super().__init__(*args)


async def verify_user(request: Request):
    if not "user" in request.session.keys():
        raise HTTPException(status_code=401, detail="Not authenticated")


class OauthData:
    CLIENT_ID: str
    CLIENT_SECRET: str
    SECRET_KEY: str

    def __init__(self):
        try:
            self.SECRET_KEY = os.environ["SECRET_KEY"]
        except KeyError as exc:
            raise OauthEnvarMissing(*exc.args) from exc

    @property
    def oauth(self) -> StarletteOAuth:
        return StarletteOAuth()

    @property
    def client(self) -> str:
        raise NotImplementedError


class GithubOAuthConfig(OauthData):
    GITHUB_ORG: str

    def __init__(self):
        super().__init__()
        try:
            self.CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
            self.CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]
            self.GITHUB_ORG = os.environ["GITHUB_ORG"]
        except KeyError as exc:
            raise OauthEnvarMissing(*exc.args) from exc

    @property
    def oauth(self) -> StarletteOAuth:
        _oauth = super().oauth
        _oauth.register(
            name="github",
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            authorize_url="https://github.com/login/oauth/authorize",
            access_token_url="https://github.com/login/oauth/access_token",
            userinfo_endpoint="https://api.github.com/user",
            api_base_url="https://api.github.com/",
        )
        return _oauth

    @property
    def client(self) -> StarletteOAuth2App:
        return self.oauth.github

    async def get_user_by_login(self, *, token: dict, login: str) -> dict:
        user = await self.client.get(f"users/{login}", token=token)
        user.raise_for_status()
        return user.json()

    async def user_is_org_member(self, *, token: dict, user_data: dict) -> bool:
        orgs = await self.client.get(user_data["organizations_url"], token=token)
        orgs.raise_for_status()
        return any(org["login"] == self.GITHUB_ORG for org in orgs.json())


OAuthConfig = GithubOAuthConfig()
