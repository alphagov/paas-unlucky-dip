from datetime import datetime, timezone
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
    field_serializer,
    field_validator,
)
from ulid import ULID


class Incident(BaseModel):
    ID: int
    title: str
    difficulty: str | None = Field(default=None)
    scenario: str

    @field_validator("scenario", "title", mode="before")
    @classmethod
    def clean_html(cls, v: str) -> str:
        return nh3.clean(
            v,
            tags={"a", "br", "h1", "h2", "h3", "h4", "strong"},
            attributes={"a": {"href"}},
            strip_comments=True,
        )


IncidentList = RootModel[List[Incident]]


class IncidentSet(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: ULID | str = Field(default_factory=ULID)
    incidents: IncidentList
    is_default: bool = Field(default=False)
    last_modified: AwareDatetime | None = Field(default=None, exclude=True)
    created: AwareDatetime = Field(
        default_factory=lambda: datetime.now(zoneinfo.gettz("UTC"))
    )
    creator: str | None = Field(default=None)

    @field_serializer("id")
    def serialize_id(self, v: ULID | str) -> str:
        if isinstance(v, ULID):
            return v.hex
        return v

    @classmethod
    def from_incident_list_json(cls, Id: str, json: str | bytes) -> "IncidentSet":
        return cls(id=Id, incidents=IncidentList.model_validate_json(json))

    @classmethod
    def from_s3_object(cls, s3_object: GetObjectOutputTypeDef) -> "IncidentSet":
        i_s = cls.model_validate_json(s3_object["Body"].read())
        i_s.last_modified = s3_object["LastModified"]
        return i_s
