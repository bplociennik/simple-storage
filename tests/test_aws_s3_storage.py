from datetime import datetime, timedelta
from os import environ
from unittest import TestCase
from uuid import uuid4

import pytest

from storages.backends.amazon_s3 import AmazonS3Storage
from storages.backends.base import Storage
from storages.exceptions import ImproperlyConfiguredError


class aws_temp_file:
    CONTENT = "Lorem ipsum dolor sit amet..."
    CONTENT_BINARY = b"Binary lorem ipsum dolor sit amet..."

    def __init__(self, storage: Storage, binary: bool = False):
        self._storage = storage
        self._binary = binary
        self._file_name = str(uuid4())

    def __enter__(self):
        self._storage.write(
            name=self._file_name,
            content=self.CONTENT_BINARY if self._binary else self.CONTENT,
            mode="xb" if self._binary else "x",
        )
        return self._file_name

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._storage.delete(self._file_name)


class TestAWSS3Storage(TestCase):
    @pytest.fixture(autouse=True)
    def init_storage(self, tmpdir):
        self._storage = AmazonS3Storage(
            aws_access_key_id=environ.get("STORAGES_AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=environ.get(
                "STORAGES_AWS_SECRET_ACCESS_KEY"
            ),
            bucket_name=environ.get("STORAGES_BUCKET_NAME"),
        )

    def test_improper_initialization(self):
        with pytest.raises(ImproperlyConfiguredError):
            AmazonS3Storage(
                aws_access_key_id="", aws_secret_access_key="", bucket_name=""
            )
        with pytest.raises(ImproperlyConfiguredError):
            AmazonS3Storage(
                aws_access_key_id="somekey",
                aws_secret_access_key="",
                bucket_name="",
            )
        with pytest.raises(ImproperlyConfiguredError):
            AmazonS3Storage(
                aws_access_key_id="some_key",
                aws_secret_access_key="some_secret",
                bucket_name="",
            )

    def test_file_not_exists(self):
        assert not self._storage.exists("some_non_existent.file")

    def test_file_exists_upon_writing(self):
        with aws_temp_file(storage=self._storage) as temp_file:
            assert self._storage.exists(temp_file)

    def test_file_contains_written_data(self):
        with aws_temp_file(storage=self._storage) as temp_file:
            assert self._storage.read(temp_file) == aws_temp_file.CONTENT

    def test_file_contains_binary_written_data(self):
        with aws_temp_file(storage=self._storage, binary=True) as temp_file:
            assert (
                self._storage.read(temp_file, mode="rb")
                == aws_temp_file.CONTENT_BINARY
            )

    def test_file_does_not_exist_upon_writing_and_deletion(self):
        with aws_temp_file(storage=self._storage) as temp_file:
            self._storage.delete(temp_file)
            assert not self._storage.exists(temp_file)

    def test_file_size_matches_content_size(self):
        with aws_temp_file(storage=self._storage) as temp_file:
            assert self._storage.size(temp_file) == len(aws_temp_file.CONTENT)

    def test_file_creation_time(self):
        with pytest.raises(NotImplementedError):
            self._storage.get_created_time("any_name.ext")

    def test_file_access_time(self):
        with pytest.raises(NotImplementedError):
            self._storage.get_access_time("any_name.ext")

    def test_file_modification_time(self):
        with aws_temp_file(storage=self._storage) as temp_file:
            modification_time = self._storage.get_modified_time(
                temp_file
            ).replace(tzinfo=None)
            assert modification_time - datetime.now() < timedelta(seconds=10)
