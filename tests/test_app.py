import importlib
from fastapi.testclient import TestClient
import src.app as appmod


def setup_module():
    # ensure module is fresh before any tests
    importlib.reload(appmod)


def test_get_activities():
    importlib.reload(appmod)
    client = TestClient(appmod.app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Basketball" in data
    assert isinstance(data["Basketball"]["participants"], list)


def test_signup_success():
    importlib.reload(appmod)
    client = TestClient(appmod.app)
    r = client.post("/activities/Tennis/signup?email=test@example.com")
    assert r.status_code == 200
    assert "Signed up test@example.com for Tennis" in r.json().get("message", "")
    data = client.get("/activities").json()
    assert "test@example.com" in data["Tennis"]["participants"]


def test_signup_duplicate():
    importlib.reload(appmod)
    client = TestClient(appmod.app)
    email = "dup@example.com"
    r1 = client.post(f"/activities/Tennis/signup?email={email}")
    assert r1.status_code == 200
    r2 = client.post(f"/activities/Tennis/signup?email={email}")
    assert r2.status_code == 400


def test_signup_full():
    importlib.reload(appmod)
    # make Tennis full by setting max_participants to current participants length
    tennis = appmod.activities["Tennis"]
    tennis["max_participants"] = len(tennis["participants"])
    client = TestClient(appmod.app)
    r = client.post("/activities/Tennis/signup?email=new@example.com")
    assert r.status_code == 400


def test_unregister_success():
    importlib.reload(appmod)
    client = TestClient(appmod.app)
    # ensure user is signed up
    client.post("/activities/Basketball/signup?email=to_remove@example.com")
    r = client.post("/activities/Basketball/unregister?email=to_remove@example.com")
    assert r.status_code == 200
    assert "Unregistered to_remove@example.com from Basketball" in r.json().get("message", "")
    data = client.get("/activities").json()
    assert "to_remove@example.com" not in data["Basketball"]["participants"]


def test_unregister_missing():
    importlib.reload(appmod)
    client = TestClient(appmod.app)
    r = client.post("/activities/Basketball/unregister?email=doesnotexist@example.com")
    assert r.status_code == 404
