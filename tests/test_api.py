"""
Integration tests for FastAPI endpoints using AAA (Arrange-Act-Assert) pattern.

Tests the following endpoints:
- GET / (redirect to static)
- GET /activities (list all activities)
- POST /activities/{activity_name}/signup (sign up for activity)
- DELETE /activities/{activity_name}/unregister (unregister from activity)
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /
        Assert: Verify redirect to /static/index.html (status 307)
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_success(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /activities
        Assert: Verify returns all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) == 9  # 9 activities in the system
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data

    def test_get_activities_response_structure(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_data, dict)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_as_list(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /activities
        Assert: Verify participants are always a list
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_happy_path(self, client):
        """
        Arrange: Valid email and activity with available spots
        Act: POST to signup endpoint
        Assert: Verify status 200 and email is added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newtag@student.example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify email was added
        all_activities = client.get("/activities").json()
        assert email in all_activities[activity_name]["participants"]

    def test_signup_multiple_students_same_activity(self, client):
        """
        Arrange: Sign up multiple different students for same activity
        Act: POST multiple signups for different emails
        Assert: All students are added successfully
        """
        # Arrange
        activity_name = "Drama Club"
        email1 = "student1@example.com"
        email2 = "student2@example.com"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        all_activities = client.get("/activities").json()
        assert email1 in all_activities[activity_name]["participants"]
        assert email2 in all_activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """
        Arrange: Non-existent activity name
        Act: POST to signup endpoint with invalid activity
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "NonExistentActivity"
        email = "student@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered(self, client):
        """
        Arrange: Email already registered for activity
        Act: POST signup with email already in participants list
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    @pytest.mark.parametrize("email", [
        "valid.email@domain.com",
        "another_valid@subdomain.co.uk",
        "simple@example.net",
    ])
    def test_signup_various_valid_emails(self, client, email):
        """
        Arrange: Various valid email formats
        Act: POST signup with different email formats
        Assert: All should succeed
        """
        # Arrange
        activity_name = "Art Studio"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        all_activities = client.get("/activities").json()
        assert email in all_activities[activity_name]["participants"]

    def test_signup_missing_email_parameter(self, client):
        """
        Arrange: Activity name provided but email parameter missing
        Act: POST to signup endpoint without email param
        Assert: Verify 422 validation error
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422  # Validation error

    def test_signup_edge_case_empty_string_email(self, client):
        """
        Arrange: Empty string as email
        Act: POST with empty email
        Assert: Email (empty string) is added as-is (API doesn't validate format)
        """
        # Arrange
        activity_name = "Tennis Club"
        email = ""
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        # API doesn't validate email format, so empty string gets added
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success_happy_path(self, client):
        """
        Arrange: Student registered for activity
        Act: DELETE to unregister endpoint
        Assert: Verify status 200 and email is removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify email was removed
        all_activities = client.get("/activities").json()
        assert email not in all_activities[activity_name]["participants"]

    def test_unregister_multiple_students(self, client):
        """
        Arrange: Multiple students registered for activity
        Act: Unregister each student one by one
        Assert: Each unregister succeeds and removes the specific student
        """
        # Arrange
        activity_name = "Chess Club"
        email1 = "michael@mergington.edu"
        email2 = "daniel@mergington.edu"
        
        # Act
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        all_activities = client.get("/activities").json()
        assert email1 not in all_activities[activity_name]["participants"]
        assert email2 not in all_activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Non-existent activity name
        Act: DELETE from unregister endpoint with invalid activity
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "NonExistentActivity"
        email = "student@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_registered(self, client):
        """
        Arrange: Email not registered for activity
        Act: DELETE with email not in participants list
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"

    def test_unregister_missing_email_parameter(self, client):
        """
        Arrange: Activity name provided but email parameter missing
        Act: DELETE without email param
        Assert: Verify 422 validation error
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        # Assert
        assert response.status_code == 422  # Validation error

    def test_unregister_then_signup_again(self, client):
        """
        Arrange: Student registered then unregistered from activity
        Act: Sign up the same student again
        Assert: Student can sign up again successfully
        """
        # Arrange
        activity_name = "Tennis Club"
        email = "ava@mergington.edu"
        
        # Act - Unregister first
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act - Sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        all_activities = client.get("/activities").json()
        assert email in all_activities[activity_name]["participants"]

    def test_unregister_edge_case_empty_string_email(self, client):
        """
        Arrange: Empty string as email to unregister
        Act: DELETE with empty email
        Assert: Returns 400 (not registered) since empty string is not in any participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = ""
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoints"""

    def test_full_signup_unregister_flow(self, client):
        """
        Arrange: New student email
        Act: Sign up, verify in list, then unregister, verify removed
        Assert: All steps succeed
        """
        # Arrange
        activity_name = "Math Olympiad"
        email = "mathwhiz@example.com"
        
        # Act & Assert - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify in list
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
        
        # Act & Assert - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_concurrent_signup_different_activities(self, client):
        """
        Arrange: One student signing up for multiple activities
        Act: Sign up for three different activities
        Assert: Student appears in all three activities
        """
        # Arrange
        email = "versatile@example.com"
        activities_to_join = ["Chess Club", "Drama Club", "Math Olympiad"]
        
        # Act
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        all_activities = client.get("/activities").json()
        for activity_name in activities_to_join:
            assert email in all_activities[activity_name]["participants"]
