import mock
from fastapi.testclient import TestClient

from api.main import app


def test_get_root():
    test_uuid = "someUUID"
    # mocked_uuid = mock.MagicMock()
    # mocked_uuid.uuid4.return_value = test_uuid
    # patcher = mock.patch("poker_pkg.poker.uuid4")
    # patcher.return_value = test_uuid

    client = client = TestClient(app)

    with mock.patch("poker_pkg.poker.uuid") as patcher:
        # patcher.return_value = test_uuid
        response = client.get("/")

    parsed_response = response.json()
    assert parsed_response["current_app_version"] == test_uuid
