"""
Comprehensive test suite for Mergington High School API

Tests all endpoints and edge cases using pytest and FastAPI's TestClient.
Structured using AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store initial state
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in plays and learn theater skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["mason@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["harper@mergington.edu", "logan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    for activity_name, activity_data in initial_activities.items():
        activities[activity_name] = activity_data.copy()
        # Deep copy participants list
        activities[activity_name]["participants"] = activity_data["participants"].copy()
    
    yield
    
    # Cleanup after test
    activities.clear()
    for activity_name, activity_data in initial_activities.items():
        activities[activity_name] = activity_data.copy()
        activities[activity_name]["participants"] = activity_data["participants"].copy()


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all 9 activities"""
        # Arrange - Activities are set up by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Debate Club" in data
        assert "Science Club" in data
    
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        # Arrange - Activities are set up by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participants_are_strings(self, client):
        """Test that participants are stored as email strings"""
        # Arrange - Activities are set up by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        for activity_name, activity_data in data.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        # Arrange
        student_email = "john@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert student_email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        # Arrange
        student_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        response = client.get("/activities")
        data = response.json()
        assert student_email in data[activity_name]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        invalid_activity = "NonExistent Club"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_signup(self, client):
        """Test that signing up twice returns 400 error"""
        # Arrange
        student_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        # Arrange
        student_email = "student@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": student_email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        assert student_email in data[activity1]["participants"]
        assert student_email in data[activity2]["participants"]
    
    def test_signup_preserves_existing_participants(self, client):
        """Test that signup doesn't remove existing participants"""
        # Arrange
        activity_name = "Chess Club"
        new_student = "newstudent@mergington.edu"
        
        response = client.get("/activities")
        original_participants = response.json()[activity_name]["participants"].copy()
        original_count = len(original_participants)
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )
        
        # Assert
        response = client.get("/activities")
        new_participants = response.json()[activity_name]["participants"]
        assert len(new_participants) == original_count + 1
        
        for participant in original_participants:
            assert participant in new_participants
    
    def test_signup_case_sensitive_activity_name(self, client):
        """Test that activity names are case-sensitive"""
        # Arrange
        student_email = "student@mergington.edu"
        wrong_case_activity = "chess club"  # Should be "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{wrong_case_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_signup_with_various_email_formats(self, client):
        """Test signup with different valid email formats"""
        # Arrange
        activity_name = "Programming Class"
        emails = [
            "student1@school.edu",
            "john.doe@mergington.edu",
            "a@b.com",
            "test+tag@domain.org"
        ]
        
        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        # Arrange
        student_email = "michael@mergington.edu"  # In Chess Club
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert student_email in data["message"]
        assert activity_name in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        # Arrange
        student_email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        response = client.get("/activities")
        data = response.json()
        assert student_email not in data[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity returns 404"""
        # Arrange
        invalid_activity = "NonExistent Club"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_student_not_signed_up(self, client):
        """Test unregister when student is not signed up returns 400"""
        # Arrange
        student_email = "notstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_preserves_other_participants(self, client):
        """Test that unregister only removes the specified participant"""
        # Arrange
        activity_name = "Chess Club"
        student_to_remove = "michael@mergington.edu"
        
        response = client.get("/activities")
        original_participants = response.json()[activity_name]["participants"].copy()
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_to_remove}
        )
        
        # Assert
        response = client.get("/activities")
        new_participants = response.json()[activity_name]["participants"]
        
        assert "daniel@mergington.edu" in new_participants  # Still there
        assert student_to_remove not in new_participants  # Removed
        assert len(new_participants) == len(original_participants) - 1
    
    def test_unregister_case_sensitive_activity_name(self, client):
        """Test that unregister is case-sensitive for activity names"""
        # Arrange
        student_email = "michael@mergington.edu"
        wrong_case_activity = "chess club"  # Should be "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{wrong_case_activity}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_twice_fails(self, client):
        """Test that unregistering twice fails on the second attempt"""
        # Arrange
        student_email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act - First unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Act - Second unregister (should fail)
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows"""
    
    def test_signup_then_unregister(self, client):
        """Test complete flow: signup then unregister"""
        # Arrange
        student_email = "integration@mergington.edu"
        activity_name = "Art Club"
        
        # Act - Sign up
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert - Verify signup
        assert response1.status_code == 200
        response = client.get("/activities")
        assert student_email in response.json()[activity_name]["participants"]
        
        # Act - Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert - Verify unregister
        assert response2.status_code == 200
        response = client.get("/activities")
        assert student_email not in response.json()[activity_name]["participants"]
    
    def test_signup_unregister_signup_again(self, client):
        """Test that a student can sign up after unregistering"""
        # Arrange
        student_email = "reregister@mergington.edu"
        activity_name = "Drama Club"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response1.status_code == 200
        
        # Act - Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response2.status_code == 200
        
        # Act - Sign up again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response3.status_code == 200
        response = client.get("/activities")
        assert student_email in response.json()[activity_name]["participants"]
    
    def test_multiple_students_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        # Arrange
        activity_name = "Debate Club"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act
        for student in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        for student in students:
            assert student in participants


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    def test_empty_email_signup(self, client):
        """Test signup with empty email"""
        # Arrange
        activity_name = "Chess Club"
        empty_email = ""
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": empty_email}
        )
        
        # Assert - Should allow empty string as FastAPI doesn't validate email format
        assert response.status_code in [200, 400, 422]
    
    def test_special_characters_in_activity_name(self, client):
        """Test that activity names with special characters are not found"""
        # Arrange
        invalid_activity = "Chess Club!"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_activities_endpoint_response_format(self, client):
        """Test that activities endpoint returns proper JSON"""
        # Arrange - No special setup
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert isinstance(response.json(), dict)
    
    def test_participant_list_modifications_isolated(self, client):
        """Test that modifying response doesn't affect server state"""
        # Arrange
        activity_name = "Chess Club"
        
        # Act - Get first response
        response1 = client.get("/activities")
        participants1 = response1.json()[activity_name]["participants"].copy()
        
        # Act - Modify the response (shouldn't affect server)
        participants1.append("hacker@evil.com")
        
        # Act - Get second response
        response2 = client.get("/activities")
        participants2 = response2.json()[activity_name]["participants"]
        
        # Assert - Server state should not be modified
        assert "hacker@evil.com" not in participants2