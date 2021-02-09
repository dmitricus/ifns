import abc
import json
import os
import typing
from unittest import mock

import requests
from requests.exceptions import RequestException


class MockResponse(abc.ABC):
    @abc.abstractmethod
    def raise_for_status(self):
        pass

    @abc.abstractmethod
    def iter_content(self, chunk_size: typing.Optional[int] = None):
        pass

    @abc.abstractmethod
    def content(self):
        pass

    @abc.abstractmethod
    def json(self) -> dict:
        pass


class SuccessResponse(MockResponse):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def __repr__(self) -> str:
        return "MockResponse()".format({self._file_path})

    @property
    def _full_path(self) -> str:
        basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(basedir, "fixtures", self._file_path)

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size: typing.Optional[int] = None):
        with open(self._full_path, "rb") as f:
            return [f.read()]

    def content(self):
        with open(self._full_path, "rb") as f:
            return [f.read()]

    def json(self) -> dict:
        with open(self._full_path) as f:
            return json.load(f)


class ErrorResponse(MockResponse):
    def __init__(self, exc: RequestException):
        self._exc = exc

    def __repr__(self) -> str:
        return "MockResponse()".format({self._exc})

    def raise_for_status(self):
        raise self._exc

    def iter_content(self, chunk_size: typing.Optional[int] = None):
        raise NotImplementedError()

    def content(self):
        raise NotImplementedError()

    def json(self) -> dict:
        raise NotImplementedError()


class MockRequests:
    def __init__(self, fixtures: typing.Dict[str, MockResponse]):
        self._fixtures = fixtures
        self._patch = None

    @classmethod
    def for_urls(cls, fixtures: typing.Dict[str, str]):
        return cls(
            {url: SuccessResponse(filepath) for url, filepath in fixtures.items()}
        )

    def __enter__(self):
        self._patch = mock.patch.object(requests, "get", self.get)
        self._patch.start()

    def __exit__(self, exc_type, exc, tb):
        if self._patch:
            self._patch.stop()

    def get(self, url, *args, **kwargs) -> MockResponse:
        if url in self._fixtures:
            return self._fixtures[url]
        raise Exception(
            "Cannot find a fixture for {}.\nAvailable fixtures: {}".format(url, self._fixtures)
        )
