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
        s3_obj = client.get_object(Key=f"{incident_set_id}.json")
    except client.exceptions.NoSuchKey as exc:
        raise ObjectNotFoundException from exc
    return IncidentSet.from_s3_object(s3_obj)


def get_all_incident_sets(
    client: DipS3Client, creator: str | None = None
) -> list[IncidentSet]:
    for o in client.get_all_objects():
        i_set = IncidentSet.from_s3_object(client.get_object(Key=o["Key"]))
        if creator is None or i_set.creator == creator:
            yield i_set


def put_incident_set(client: DipS3Client, incident_set: IncidentSet) -> None:
    if isinstance(incident_set.id, str):
        file_id = incident_set.id
    else:
        file_id = incident_set.id.hex

    return client.put_object(
        Key=f"{file_id}.json",
        Body=incident_set.model_dump_json().encode("utf-8"),
    )


def delete_incident_set(client: DipS3Client, incident_set_id: str) -> None:
    return client.delete_object(Key=f"{incident_set_id}.json")
