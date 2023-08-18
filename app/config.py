from app.models import Config as ConfigModel
from app.s3 import DipS3Client, S3Client


class ConfigController:
    client: DipS3Client
    config: ConfigModel

    def __init__(self, client: DipS3Client) -> None:
        self.client = client
        try:
            cfg = client.get_object(Key="config.json")
            self.config = ConfigModel.model_validate_json(
                cfg["Body"].read().decode("utf-8")
            )
        except client.exceptions.NoSuchKey:
            self.config = ConfigModel()
            self.client.put_object(
                Key="config.json", Body=self.config.model_dump_json().encode("utf-8")
            )

    @property
    def default_id(self):
        return self.config.default_id

    @property
    def default_creator(self):
        return self.config.default_creator

    def is_admin(self, user: str) -> bool:
        return user in self.config.admin_users


Config = ConfigController(S3Client)
