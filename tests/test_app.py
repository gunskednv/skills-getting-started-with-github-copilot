"""
Tests for the Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
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
        "Soccer Team": {
            "description": "Join the school soccer team and compete in local matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ethan@mergington.edu", "ava@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["charlotte@mergington.edu", "noah@mergington.edu"]
        },
        "Mathletes": {
            "description": "Compete in math competitions and solve challenging problems",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["oliver@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["elijah@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_signed_up(self, client):
        """Test signup when student is already registered"""
        # First signup
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is already signed up"
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        # First, add a participant
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Then remove them
        response = client.delete("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Removed newstudent@mergington.edu from Chess Club" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_remove_existing_participant(self, client):
        """Test removing a participant that was already in the activity"""
        # Remove an existing participant
        response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_remove_participant_activity_not_found(self, client):
        """Test removing participant from non-existent activity"""
        response = client.delete("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_participant_not_in_activity(self, client):
        """Test removing participant who is not registered"""
        response = client.delete("/activities/Chess Club/signup?email=notregistered@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Participant not found in this activity"
    
    def test_remove_participant_with_special_characters(self, client):
        """Test removal with URL-encoded activity name"""
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        response = client.delete("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200


class TestEndToEndWorkflow:
    """End-to-end tests for complete workflows"""
    
    def test_signup_and_remove_workflow(self, client):
        """Test complete workflow of signing up and removing a participant"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup_response = client.get("/activities")
        after_signup_count = len(after_signup_response.json()[activity]["participants"])
        assert after_signup_count == initial_count + 1
        assert email in after_signup_response.json()[activity]["participants"]
        
        # Remove
        remove_response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        after_removal_response = client.get("/activities")
        after_removal_count = len(after_removal_response.json()[activity]["participants"])
        assert after_removal_count == initial_count
        assert email not in after_removal_response.json()[activity]["participants"]
    
    def test_multiple_signups_different_activities(self, client):
        """Test signing up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        response3 = client.post(f"/activities/Soccer Team/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # Verify all signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]
        assert email in activities_data["Soccer Team"]["participants"]
