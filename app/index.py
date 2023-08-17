from app.models import IncidentSet
from app.models import Index as IndexModel, UUID4
from app.s3 import DipS3Client, S3Client


class IncidentSetIndex:
    client: DipS3Client
    index: IndexModel

    def __init__(self, client: DipS3Client) -> None:
        self.client = client

        try:
            index = client.get_object(Key="index.json")
            self.index = IndexModel.model_validate_json(index["Body"].read())
        except client.exceptions.NoSuchKey:
            self.index = IndexModel()
            self.commit()

    def commit(self) -> None:
        self.client.put_object(
            Key="index.json", Body=self.index.model_dump_json().encode("utf-8")
        )

    def add_incident_set(self, incident_set: IncidentSet) -> None:
        self.index.add_to_index(incident_set.creator, incident_set.id)
        self.commit()

    def remove_incident_set(self, incident_set: IncidentSet | UUID4) -> None:
        if isinstance(incident_set, IncidentSet):
            incident_set = incident_set.id
        try:
            self.index.remove_from_index(incident_set)
        except KeyError:
            pass
        self.commit()

    def ids(self, *creators) -> list[str]:
        for creator in creators:
            yield from self.index.forward.get(creator, [])

    def get_creator(self, incident_set_id: str) -> str:
        return self.index.reverse[incident_set_id]


Index = IncidentSetIndex(S3Client)
