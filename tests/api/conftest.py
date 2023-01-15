import pytest
from fastapi.testclient import TestClient

from api.api import create_app


@pytest.fixture
def api_app():
    return create_app()


@pytest.fixture
def api_client(api_app):
    return TestClient(api_app)
