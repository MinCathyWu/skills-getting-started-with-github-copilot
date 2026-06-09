import copy
from urllib.parse import quote

from fastapi.testclient import TestClient
import pytest

from src import app as application


ORIGINAL = copy.deepcopy(application.activities)
client = TestClient(application.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset in-memory activities before each test
    application.activities = copy.deepcopy(ORIGINAL)
    yield
    application.activities = copy.deepcopy(ORIGINAL)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate():
    activity = "Chess Club"
    email = "test.user@example.com"
    resp = client.post(f"/activities/{quote(activity)}/signup?email={email}")
    assert resp.status_code == 200
    assert email in application.activities[activity]["participants"]

    # duplicate signup should fail
    resp2 = client.post(f"/activities/{quote(activity)}/signup?email={email}")
    assert resp2.status_code == 400


def test_remove_participant():
    activity = "Programming Class"
    email = "remove.me@example.com"

    # sign up then remove
    r = client.post(f"/activities/{quote(activity)}/signup?email={email}")
    assert r.status_code == 200

    r2 = client.delete(f"/activities/{quote(activity)}/participants?email={email}")
    assert r2.status_code == 200
    assert email not in application.activities[activity]["participants"]
