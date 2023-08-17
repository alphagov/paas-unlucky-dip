from datetime import datetime
from typing import List

from dateutil import zoneinfo

import nh3
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    PlainSerializer,
    BeforeValidator,
)
from ulid import ULID as ORIGINAL_ULID

from typing_extensions import Annotated


def validate_ulid(v: ORIGINAL_ULID | str) -> ORIGINAL_ULID:
    if isinstance(v, ORIGINAL_ULID):
        return v
    return ORIGINAL_ULID.from_hex(v)


ULID = Annotated[
    ORIGINAL_ULID,
    Field(default_factory=ORIGINAL_ULID),
    BeforeValidator(validate_ulid),
    PlainSerializer(lambda x: x.hex, when_used="json-unless-none"),
]


class Config(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    default_id: ULID = Field(default_factory=ULID)
    default_creator: str = Field(default="system")


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

    id: ULID
    incidents: IncidentList

    creator: str = Field(default="system")
    last_modified: AwareDatetime | None = Field(default=None, exclude=True)
    created: AwareDatetime = Field(
        default_factory=lambda: datetime.now(zoneinfo.gettz("UTC"))
    )

    @property
    def id_hex(self) -> str:
        return self.id.hex

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

    forward: dict[str, List[str]] = {}
    reverse: dict[str, str] = {}

    def add_to_index(self, user: str, incident_set_id: ULID) -> None:
        incident_set_id = incident_set_id.hex

        self.forward.setdefault(user, []).append(incident_set_id)
        self.reverse[incident_set_id] = user

    def remove_from_index(self, incident_set_id: ULID) -> None:
        incident_set_id = incident_set_id.hex

        user = self.reverse[incident_set_id]
        self.forward[user].remove(incident_set_id)
        del self.reverse[incident_set_id]
