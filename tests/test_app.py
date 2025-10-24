import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities


initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # reset the in-memory activities dict before each test
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities():
    client = TestClient(app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_reflects_immediately():
    client = TestClient(app)
    email = "testuser@example.com"
    r = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")
    r2 = client.get("/activities")
    assert email in r2.json()["Chess Club"]["participants"]


def test_unregister_and_reflects_immediately():
    client = TestClient(app)
    email = "tempuser@example.com"
    # add first
    r1 = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert r1.status_code == 200
    # now remove
    r = client.post("/activities/Chess%20Club/unregister", params={"email": email})
    assert r.status_code == 200
    assert "Removed" in r.json().get("message", "")
    r2 = client.get("/activities")
    assert email not in r2.json()["Chess Club"]["participants"]
