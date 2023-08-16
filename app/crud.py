from pathlib import Path

from .models import IncidentSet
from .s3 import DipS3Client


class ObjectNotFoundException(Exception):
    pass


def init_default_incident_set(
    client: DipS3Client,
    default_incident_set_file: Path,
    incident_set_id: str = "default",
) -> None:
    try:
        get_incident_set(client=client, incident_set_id=incident_set_id)
    except ObjectNotFoundException:
        incident_set = (IncidentSet(id=incident_set_id, incidents=[]),)

        if default_incident_set_file.is_file():
            incident_set = IncidentSet.from_incident_list_json(
                incident_set_id, default_incident_set_file.read_text()
            )
        incident_set.is_default = True

        return put_incident_set(client=client, incident_set=incident_set)


def get_incident_set(client: DipS3Client, incident_set_id: str) -> IncidentSet:
    try:
        blob = client.get_object(Key=f"{incident_set_id}.json")
    except client.exceptions.NoSuchKey as exc:
        raise ObjectNotFoundException from exc
    return IncidentSet.model_validate_json(blob)


def put_incident_set(client: DipS3Client, incident_set: IncidentSet) -> None:
    return client.put_object(
        Key=f"{incident_set.id}.json",
        Body=incident_set.model_dump_json().encode("utf-8"),
    )
