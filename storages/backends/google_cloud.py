from datetime import datetime
from typing import AnyStr

from google.cloud.storage import Client

from storages.backends.base import Storage


class GoogleCloudStorage(Storage):
    _TYPE = "service_account"
    _AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    _TOKEN_URI = "https://oauth2.googleapis.com/token"
    _AUTH_PROVIDER_CERT_URI = "https://www.googleapis.com/oauth2/v1/certs"

    def __init__(
        self,
        gcs_project_id: str,
        gcs_private_key_id: str,
        gcs_private_key: str,
        gcs_client_email: str,
        gcs_client_id: str,
        gcs_client_x509_cert_url: str,
        gcs_bucket: str,
        gcs_type: str = _TYPE,
        gcs_auth_uri: str = _AUTH_URI,
        gcs_token_uri: str = _TOKEN_URI,
        gcs_auth_provider_x509_cert_url: str = _AUTH_PROVIDER_CERT_URI,
    ):
        print(gcs_private_key)
        info = dict(
            type=gcs_type,
            project_id=gcs_project_id,
            private_key_id=gcs_private_key_id,
            private_key=gcs_private_key,
            client_email=gcs_client_email,
            client_id=gcs_client_id,
            auth_uri=gcs_auth_uri,
            token_uri=gcs_token_uri,
            auth_provider_x509_cert_url=gcs_client_x509_cert_url,
            client_x509_cert_url=gcs_auth_provider_x509_cert_url,
        )
        self._client = Client.from_service_account_info(info=info)
        self._bucket = self._client.bucket(bucket_name=gcs_bucket)

    def read(self, name: str, mode: str = "r") -> AnyStr:
        blob = self._bucket.get_blob(name)
        if "b" in mode:
            return blob.download_as_bytes()
        return blob.download()

    def write(self, name: str, content: AnyStr, mode: str = "a"):
        pass

    def delete(self, name: str):
        pass

    def exists(self, name: str) -> bool:
        pass

    def size(self, name: str) -> int:
        pass

    def get_created_time(self, name: str) -> datetime:
        pass

    def get_modified_time(self, name: str) -> datetime:
        pass

    def get_access_time(self, name: str) -> datetime:
        pass
