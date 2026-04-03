"""
Pytest configuration and shared fixtures for tests.

Provides:
- TestClient for API testing
- Fresh in-memory activities data for each test (isolation)
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Arrange: Provide a TestClient instance with fresh in-memory data per test.
    
    This fixture ensures each test runs with a clean slate by resetting the
    activities dictionary to its initial state before and after each test.
    """
    # Arrange: Save original state
    original_activities = copy.deepcopy(activities)
    
    # Provide the client for the test
    yield TestClient(app)
    
    # Cleanup: Restore original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activities():
    """
    Arrange: Provide reference data about expected activities structure.
    
    Useful for tests that need to verify activity properties without
    making unnecessary API calls.
    """
    return {
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
    }
