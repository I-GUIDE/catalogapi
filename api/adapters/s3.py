import boto3
import json
from botocore.client import Config
from botocore import UNSIGNED

from api.adapters.base import AbstractRepositoryMetadataAdapter, AbstractRepositoryRequestHandler
from api.adapters.utils import RepositoryType, register_adapter
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission


class _S3RequestHandler(AbstractRepositoryRequestHandler):
    
    def get_metadata(self, record_id: str):
        endpoint_url = record_id.split("+")[0]
        bucket_name = record_id.split("+")[1]
        file_key = record_id.split("+")[2]

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), endpoint_url=endpoint_url)
        
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        json_content = response['Body'].read().decode('utf-8')

        # Parse the JSON content
        data = json.loads(json_content)

        return data


class S3MetadataAdapter(AbstractRepositoryMetadataAdapter):
    repo_api_handler = _S3RequestHandler()

    @staticmethod
    def to_catalog_record(metadata: dict) -> DatasetMetadataDOC:
        return DatasetMetadataDOC(**metadata)

    @staticmethod
    def to_repository_record(catalog_record: DatasetMetadataDOC):
        """Converts dataset catalog record to hydroshare resource metadata"""
        raise NotImplementedError

    @staticmethod
    def update_submission(submission: Submission, repo_record_id: str) -> Submission:
        """Sets additional hydroshare specific metadata to submission record"""

        submission.repository_identifier = repo_record_id
        submission.repository = RepositoryType.S3
        return submission


register_adapter(RepositoryType.S3, S3MetadataAdapter)
