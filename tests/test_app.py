"""
Pytest tests for the FastAPI High School Management System API.
Each test follows Arrange-Act-Assert and resets state between tests.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

BASE_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity state before each test."""
    yield
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert expected_activity in response.json()
        assert isinstance(response.json(), dict)

    def test_get_activities_has_expected_fields(self, client):
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        first_activity = next(iter(response.json().values()))

        # Assert
        assert response.status_code == 200
        assert set(first_activity.keys()) == expected_fields


class TestSignupForActivity:
    def test_signup_for_existing_activity_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        original_participants = list(activities[activity_name]["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

        # Assert
        assert response.status_code == 200
        assert new_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(original_participants) + 1

    def test_signup_for_duplicate_participant_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_email = activities[activity_name]["participants"][0]

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    def test_remove_existing_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        participant_email = activities[activity_name]["participants"][0]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants", params={"email": participant_email}
        )

        # Assert
        assert response.status_code == 200
        assert participant_email not in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"

    def test_remove_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        participant_email = "missing@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants", params={"email": participant_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
