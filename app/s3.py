import json
import os

import boto3
from mypy_boto3_s3.client import Exceptions
from mypy_boto3_s3.client import S3Client as S3ClientType


class DipS3Client:
    client: S3ClientType
    bucket: str

    def __init__(self) -> None:
        vcap_services = json.loads(os.environ["VCAP_SERVICES"])
        s3_creds = vcap_services["aws-s3-bucket"][0]["credentials"]
        self.bucket = s3_creds["bucket_name"]

        client_params = {
            "aws_access_key_id": s3_creds["aws_access_key_id"],
            "aws_secret_access_key": s3_creds["aws_secret_access_key"],
        }
        if "AWS_ENDPOINT" in os.environ:
            client_params["endpoint_url"] = os.environ["AWS_ENDPOINT"]

        self.client = boto3.client("s3", **client_params)

    @property
    def exceptions(self) -> Exceptions:
        return self.client.exceptions

    def get_object(self, Key: str):
        res = self.client.get_object(Bucket=self.bucket, Key=Key)
        return res

    def get_all_objects(self, Prefix: str = ""):
        paginator = self.client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=self.bucket, Prefix=Prefix)
        for page in page_iterator:
            if "Contents" in page:
                yield from page["Contents"]

    def put_object(self, Key: str, Body: bytes, **kwargs):
        return self.client.put_object(Bucket=self.bucket, Key=Key, Body=Body, **kwargs)

    def delete_object(self, Key: str):
        return self.client.delete_object(Bucket=self.bucket, Key=Key)


S3Client = DipS3Client()
