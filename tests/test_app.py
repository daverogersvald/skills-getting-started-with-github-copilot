"""Tests for the Mergington High School API (src/app.py)."""

from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (302, 307)
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_returns_all_activities(self, client):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert set(data) == set(activities)

    def test_activity_structure(self, client):
        data = client.get("/activities").json()
        chess = data["Chess Club"]
        assert chess["description"] == (
            "Learn strategies and compete in chess tournaments"
        )
        assert chess["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess["max_participants"] == 12
        assert chess["participants"] == [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ]


class TestSignup:
    def test_signup_success(self, client):
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Signed up newstudent@mergington.edu for Basketball Team"
        }
        assert (
            "newstudent@mergington.edu"
            in activities["Basketball Team"]["participants"]
        )

    def test_signup_duplicate_email(self, client):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Student already signed up for this activity"
        )

    def test_signup_unknown_activity(self, client):
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "someone@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_missing_email(self, client):
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422


class TestUnregister:
    def test_unregister_success(self, client):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Unregistered michael@mergington.edu from Chess Club"
        }
        assert (
            "michael@mergington.edu"
            not in activities["Chess Club"]["participants"]
        )

    def test_unregister_not_signed_up(self, client):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "stranger@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Student is not signed up for this activity"
        )

    def test_unregister_unknown_activity(self, client):
        response = client.delete(
            "/activities/Nonexistent Club/signup",
            params={"email": "someone@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestStateIsolation:
    def test_signup_state_reset_between_tests(self, client):
        # If reset_activities works, Basketball Team is empty again here
        # even though test_signup_success added a participant.
        assert activities["Basketball Team"]["participants"] == []
