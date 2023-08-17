from pathlib import Path

from app.models import ULID, IncidentList, IncidentSet
from app.s3 import DipS3Client

from app.index import Index
from app.config import Config


class ObjectNotFoundException(Exception):
    pass


def s3_key_from_incident_set_id(incident_set_id: ULID) -> str:
    return f"incident_sets/{incident_set_id.to_uuid()}.json"


def s3_key_from_incident_set(incident_set: IncidentSet) -> str:
    return s3_key_from_incident_set_id(incident_set.id)


def init_default_incident_set(
    client: DipS3Client,
    default_incident_set_file: Path,
) -> None:
    try:
        get_incident_set(client=client, incident_set_id=Config.default_id)
    except ObjectNotFoundException:
        incident_set = IncidentSet.model_construct(
            id=Config.default_id,
            creator=Config.default_creator,
            incidents=[],
        )

        if default_incident_set_file.is_file():
            incidents = IncidentList.model_validate_json(
                default_incident_set_file.read_text()
            )
            incident_set.incidents = incidents

        return put_incident_set(client=client, incident_set=incident_set)


def get_incident_set(client: DipS3Client, incident_set_id: ULID | str) -> IncidentSet:
    if isinstance(incident_set_id, str):
        incident_set_id = ULID.from_hex(incident_set_id)  # pylint: disable=no-member
    try:
        s3_obj = client.get_object(Key=s3_key_from_incident_set_id(incident_set_id))
    except client.exceptions.NoSuchKey as exc:
        Index.remove_incident_set(incident_set_id)
        raise ObjectNotFoundException from exc
    return IncidentSet.from_s3_object(s3_obj)


def get_all_incident_sets(client: DipS3Client, creator: str | None = None):
    for i in Index.ids(creator=creator):
        try:
            yield get_incident_set(client=client, incident_set_id=i)
        except ObjectNotFoundException:
            pass


def put_incident_set(client: DipS3Client, incident_set: IncidentSet) -> None:
    res = client.put_object(
        Key=s3_key_from_incident_set(incident_set),
        Body=incident_set.model_dump_json().encode("utf-8"),
    )
    Index.add_incident_set(incident_set)
    return res


def delete_incident_set(
    client: DipS3Client,
    incident_set_id: ULID | str,
):
    if isinstance(incident_set_id, str):
        incident_set_id = ULID.from_hex(incident_set_id)  # pylint: disable=no-member
    res = client.delete_object(Key=s3_key_from_incident_set_id(incident_set_id))
    Index.remove_incident_set(incident_set_id)
    return res
