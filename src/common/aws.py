from os import remove
from typing import Union

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from common import ProgressPercentage


class AwsClient:

    def __init__(
        self, resource: str, access_key: str, secret_access_key: str, region: str
    ):
        self.resource = resource
        self.region = region
        self.client = boto3.client(
            service_name=resource,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )

    def get_buckets(self) -> Union[list, dict]:
        """Get buckets

        Returns: a list of buckets and details of AWS account

        """
        if self.resource == "s3":
            return self.client.list_buckets()
        else:
            name = "The resource is not S3 bucket"
            logger.info(name)
            return {"status": name}

    def upload_file(
        self,
        filename: str,
        bucket: str,
        object_name: str = None,
        public_file: bool = True,
    ) -> dict:
        """Upload a file to an S3 bucket

        Args:

            - file_name: File to upload
            - bucket: Bucket to upload to
            - object_name: S3 object name. If not specified then file_name is used

        Returns: True if file was uploaded, else False
        """

        # Upload the file
        try:
            if public_file:
                response = self.client.upload_file(
                    f"files/{filename}",
                    bucket,
                    object_name,
                    ExtraArgs={"ACL": "public-read"},
                )
            else:
                response = self.client.upload_file(
                    f"files/{filename}", bucket, object_name
                )
            logger.info(response)

        except ClientError as e:
            logger.error(e)
            return {
                "status": False,
                "file": filename,
                "object_name": object_name,
                "url": f"https://{bucket}.s3.{self.region}.amazonaws.com/{object_name}",
            }
        finally:
            remove(f"files/{filename}")
        return {
            "status": True,
            "object_name": object_name,
            "url": f"https://{bucket}.s3.{self.region}.amazonaws.com/{object_name}",
        }

    def delete_file(
        self,
        bucket: str,
        object_name: str,
    ):
        try:
            response = self.client.delete_object(Bucket=bucket, Key=object_name)
            logger.info(response)
            return {"status": response.get("DeleteMarker"), "url": object_name}
        except ClientError as e:
            logger.error(e)
            return {"status": False, "url": object_name}

    def create_presigned_url(self, bucket_name, object_name, expiration=3600) -> str:
        """Generate a presigned URL to share an S3 object

        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """

        # Generate a presigned URL for the S3 object
        try:
            response = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )
        except ClientError as e:
            logger.error(e)
            return None

        # The response contains the presigned URL
        return response
