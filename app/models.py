from typing import List

from pydantic import BaseModel, Field, RootModel, field_validator

import nh3


class Incident(BaseModel):
    ID: int
    title: str
    difficulty: str | None = Field(default=None)
    scenario: str

    @field_validator("scenario", mode="before")
    @classmethod
    def clean_scenario(cls, v: str) -> str:
        return nh3.clean(
            v,
            tags={"a", "br", "h1", "h2", "h3", "h4", "strong"},
            attributes={"a": {"href"}},
            strip_comments=True,
        )


IncidentList = RootModel[List[Incident]]


class IncidentSet(BaseModel):
    id: str
    incidents: IncidentList
    is_default: bool = Field(default=False)

    @classmethod
    def from_incident_list_json(cls, Id: str, json: str | bytes) -> "IncidentSet":
        return cls(id=Id, incidents=IncidentList.model_validate_json(json))
