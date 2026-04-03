"""
Unit tests for business logic and helper functions using AAA pattern.

These tests focus on specific business rules and data validation
that could be extracted into helper functions.
"""

import pytest


class TestActivityValidation:
    """Unit tests for activity validation logic"""

    def test_activity_exists_in_system(self, client):
        """
        Arrange: Known activity name
        Act: Check if activity exists by fetching all activities
        Assert: Activity is in the response
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        all_activities = client.get("/activities").json()
        
        # Assert
        assert activity_name in all_activities

    def test_activity_not_exists_in_system(self, client):
        """
        Arrange: Non-existent activity name
        Act: Check if activity exists by fetching all activities
        Assert: Activity is not in the response
        """
        # Arrange
        activity_name = "NonExistent"
        
        # Act
        all_activities = client.get("/activities").json()
        
        # Assert
        assert activity_name not in all_activities

    def test_all_nine_activities_exist(self, client):
        """
        Arrange: Expected set of 9 activities
        Act: Fetch all activities
        Assert: All 9 activities are present
        """
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Drama Club", "Art Studio", "Math Olympiad", "Debate Club"
        ]
        
        # Act
        all_activities = client.get("/activities").json()
        
        # Assert
        for activity in expected_activities:
            assert activity in all_activities
        assert len(all_activities) == 9


class TestParticipantValidation:
    """Unit tests for participant list logic"""

    def test_participant_already_registered_check(self, client):
        """
        Arrange: Email known to be registered for an activity
        Act: Fetch activities and check participants list
        Assert: Email is in participants list
        """
        # Arrange
        activity_name = "Chess Club"
        registered_email = "michael@mergington.edu"
        
        # Act
        all_activities = client.get("/activities").json()
        participants = all_activities[activity_name]["participants"]
        
        # Assert
        assert registered_email in participants

    def test_participant_not_registered_check(self, client):
        """
        Arrange: Email not registered for an activity
        Act: Fetch activities and check participants list
        Assert: Email is not in participants list
        """
        # Arrange
        activity_name = "Chess Club"
        unregistered_email = "notregistered@example.com"
        
        # Act
        all_activities = client.get("/activities").json()
        participants = all_activities[activity_name]["participants"]
        
        # Assert
        assert unregistered_email not in participants

    def test_participants_list_is_mutable_across_signups(self, client):
        """
        Arrange: Fresh client
        Act: Sign up a new participant
        Assert: Participants list increases by one
        """
        # Arrange
        activity_name = "Tennis Club"
        new_email = "newparticipant@example.com"
        
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        activities_after = client.get("/activities").json()
        final_count = len(activities_after[activity_name]["participants"])
        assert final_count == initial_count + 1

    def test_participants_list_decreases_on_unregister(self, client):
        """
        Arrange: Participant registered for activity
        Act: Unregister the participant
        Assert: Participants list decreases by one
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity_name]["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        activities_after = client.get("/activities").json()
        final_count = len(activities_after[activity_name]["participants"])
        assert final_count == initial_count - 1


class TestActivityCapacity:
    """Unit tests for capacity-related logic"""

    def test_activity_has_capacity_info(self, client):
        """
        Arrange: Any activity
        Act: Fetch activities
        Assert: Each activity has max_participants defined
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        all_activities = client.get("/activities").json()
        activity = all_activities[activity_name]
        
        # Assert
        assert "max_participants" in activity
        assert isinstance(activity["max_participants"], int)
        assert activity["max_participants"] > 0

    def test_current_participant_count_below_capacity(self, client):
        """
        Arrange: Any activity
        Act: Fetch activities
        Assert: Current participants <= max_participants
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        all_activities = client.get("/activities").json()
        activity = all_activities[activity_name]
        
        # Assert
        current_count = len(activity["participants"])
        max_capacity = activity["max_participants"]
        assert current_count <= max_capacity

    @pytest.mark.parametrize("activity_name", [
        "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
        "Tennis Club", "Drama Club", "Art Studio", "Math Olympiad", "Debate Club"
    ])
    def test_all_activities_respect_capacity(self, client, activity_name):
        """
        Arrange: All activities in system
        Act: Fetch activities
        Assert: All activities have participants <= max_participants
        """
        # Act
        all_activities = client.get("/activities").json()
        activity = all_activities[activity_name]
        
        # Assert
        current_count = len(activity["participants"])
        max_capacity = activity["max_participants"]
        assert current_count <= max_capacity, \
            f"{activity_name} has {current_count} participants but max is {max_capacity}"


class TestActivityDataStructure:
    """Unit tests for activity data structure and fields"""

    def test_activity_has_all_required_fields(self, client):
        """
        Arrange: Any activity
        Act: Fetch activities
        Assert: Each activity has all required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        activity_name = "Chess Club"
        
        # Act
        all_activities = client.get("/activities").json()
        activity = all_activities[activity_name]
        
        # Assert
        for field in required_fields:
            assert field in activity, f"Activity missing required field: {field}"

    def test_activity_fields_have_correct_types(self, client):
        """
        Arrange: Any activity
        Act: Fetch activities and check field types
        Assert: All fields have correct types
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        all_activities = client.get("/activities").json()
        activity = all_activities[activity_name]
        
        # Assert
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)

    def test_participants_are_all_strings(self, client):
        """
        Arrange: Any activity
        Act: Fetch activities
        Assert: All participants are strings (email addresses)
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        all_activities = client.get("/activities").json()
        participants = all_activities[activity_name]["participants"]
        
        # Assert
        for participant in participants:
            assert isinstance(participant, str)

    def test_non_empty_fields_are_truly_non_empty(self, client):
        """
        Arrange: All activities
        Act: Fetch activities
        Assert: String fields are not empty
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        all_activities = client.get("/activities").json()
        activity = all_activities[activity_name]
        
        # Assert
        assert len(activity["description"]) > 0
        assert len(activity["schedule"]) > 0
        assert activity["max_participants"] > 0


class TestResponseConsistency:
    """Unit tests for response consistency across multiple calls"""

    def test_activities_response_consistent_between_calls(self, client):
        """
        Arrange: Fresh client
        Act: Call GET /activities twice
        Assert: Same response both times (no data changed)
        """
        # Act
        response1 = client.get("/activities").json()
        response2 = client.get("/activities").json()
        
        # Assert
        assert response1 == response2

    def test_signup_response_format_consistency(self, client):
        """
        Arrange: New email for signup
        Act: Sign up for activity
        Assert: Response has expected format with 'message' key
        """
        # Arrange
        activity_name = "Art Studio"
        email = "test@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_unregister_response_format_consistency(self, client):
        """
        Arrange: Registered participant
        Act: Unregister from activity
        Assert: Response has expected format with 'message' key
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_error_response_format_consistency(self, client):
        """
        Arrange: Invalid activity name
        Act: Try to signup for non-existent activity
        Assert: Error response has 'detail' key
        """
        # Arrange
        activity_name = "InvalidActivity"
        email = "test@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert isinstance(data, dict)
        assert "detail" in data
