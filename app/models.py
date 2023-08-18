from __future__ import annotations

import os
from datetime import datetime
from typing import List
from uuid import uuid4

import nh3
from dateutil import zoneinfo
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef
from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    RootModel,
    field_validator,
)


class Config(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    default_id: UUID4 = Field(default_factory=uuid4)
    default_creator: str = Field(default="_system")

    @property
    def admin_users(self) -> list[str]:
        return os.getenv("ADMIN_USERS", "").split(",")


class Incident(BaseModel):
    ID: int
    title: str
    difficulty: str | None = Field(default=None)
    scenario: str

    @field_validator("scenario", "title", mode="before")
    @classmethod
    def clean_html(cls, v: str) -> str:
        return nh3.clean(  # pylint: disable=no-member
            v,
            tags={"a", "br", "h1", "h2", "h3", "h4", "strong"},
            attributes={"a": {"href"}},
            strip_comments=True,
        )


IncidentList = RootModel[List[Incident]]


class IncidentSetUpdateBody(BaseModel):
    incidents: IncidentList
    name: str | None = Field(default=None)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip() if v.strip() else None


class IncidentSet(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID4 = Field(default_factory=uuid4)
    name: str | None = Field(default=None)
    incidents: IncidentList

    creator: str | None = Field(default=None)
    last_modified: AwareDatetime | None = Field(default=None, exclude=True)
    created: AwareDatetime = Field(
        default_factory=lambda: datetime.now(zoneinfo.gettz("UTC"))
    )

    @property
    def display_name(self) -> str:
        if self.name:
            return self.name
        return str(self.id)

    @field_validator("name", mode="before")
    @classmethod
    def clean_html(cls, v: str) -> str:
        return nh3.clean(  # pylint: disable=no-member
            v,
            strip_comments=True,
        )

    @classmethod
    def from_incident_list_json(cls, Id: str, json: str | bytes) -> "IncidentSet":
        return cls(id=Id, incidents=IncidentList.model_validate_json(json))

    @classmethod
    def from_s3_object(cls, s3_object: GetObjectOutputTypeDef) -> "IncidentSet":
        i_s = cls.model_validate_json(s3_object["Body"].read())
        i_s.last_modified = s3_object["LastModified"]
        return i_s


class Index(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    forward: dict[str, List[UUID4]] | dict[str, dict[UUID4, None]] = {}
    reverse: dict[UUID4, str] = {}

    def add_to_index(self, user: str, incident_set_id: UUID4) -> None:
        self.forward.setdefault(user, [])[incident_set_id] = None
        self.reverse[incident_set_id] = user

    def remove_from_index(self, incident_set_id: UUID4) -> None:
        user = self.reverse[incident_set_id]
        del self.forward[user][incident_set_id]
        del self.reverse[incident_set_id]


class GithubUser(BaseModel):
    login: str
    id: int
    avatar_url: HttpUrl | None = None
    url: HttpUrl
    html_url: HttpUrl
    organizations_url: HttpUrl

    def sized_avatar_url(self, size: int = 32) -> HttpUrl | None:
        if self.avatar_url is None:
            return None
        if self.avatar_url.query:
            return HttpUrl(f"{self.avatar_url}&s={size}")
        return HttpUrl(f"{self.avatar_url}?s={size}")
