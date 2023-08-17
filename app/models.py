from datetime import datetime
from typing import List
from uuid import uuid4

import os

import nh3
from dateutil import zoneinfo
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef
from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
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


class IncidentSet(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID4 = Field(default_factory=uuid4)
    incidents: IncidentList

    creator: str | None = Field(default=None)
    last_modified: AwareDatetime | None = Field(default=None, exclude=True)
    created: AwareDatetime = Field(
        default_factory=lambda: datetime.now(zoneinfo.gettz("UTC"))
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

    forward: dict[str, List[UUID4]] = {}
    reverse: dict[UUID4, str] = {}

    def add_to_index(self, user: str, incident_set_id: UUID4) -> None:
        self.forward.setdefault(user, []).append(incident_set_id)
        self.reverse[incident_set_id] = user

    def remove_from_index(self, incident_set_id: UUID4) -> None:
        user = self.reverse[incident_set_id]
        self.forward[user].remove(incident_set_id)
        del self.reverse[incident_set_id]
