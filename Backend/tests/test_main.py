# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app
import json
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Mock Firebase Auth
@pytest.fixture
def mock_firebase_auth():
    with patch('firebase_admin.auth.verify_id_token') as mock_verify:
        mock_verify.return_value = {"uid": "test-user-123"}
        yield mock_verify

@pytest.fixture
def mock_admin_auth():
    with patch('firebase_admin.auth.verify_id_token') as mock_verify:
        mock_verify.return_value = {"uid": "admin-user-123"}
        
        # Also mock the get_user function
        with patch('firebase_admin.auth.get_user') as mock_get_user:
            mock_user = MagicMock()
            mock_user.custom_claims = {"admin": True}
            mock_get_user.return_value = mock_user
            yield mock_verify

# Mock headers
@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer fake-token-123"}

@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer fake-admin-token-123"}

# Test Game Configuration
def test_create_game_configuration(mock_firebase_auth, auth_headers):
    # Sample configuration
    sample_config = {
        "title": "Test Game",
        "description": "A test game configuration",
        "difficulty_levels": [
            {
                "level_name": "Easy",
                "target_min": 5,
                "target_max": 10,
                "addends": [
                    {"min_value": 1, "max_value": 5},
                    {"min_value": 1, "max_value": 5}
                ],
                "time_limit": None,
                "hints_available": True
            }
        ],
        "starting_level": "Easy",
        "public": True,
        "feedback_sensitivity": 1.0,
        "progression_criteria": {}
    }
    
    response = client.post(
        "/game-configurations/",
        json=sample_config,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Game"
    assert data["created_by"] == "test-user-123"
    
    # Test retrieving the created configuration
    config_id = data["id"]
    get_response = client.get(
        f"/game-configurations/{config_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["title"] == "Test Game"

def test_list_game_configurations(mock_firebase_auth, auth_headers):
    response = client.get(
        "/game-configurations/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_game_configuration(mock_firebase_auth, auth_headers):
    # First create a configuration
    sample_config = {
        "title": "Test Game",
        "description": "A test game configuration",
        "difficulty_levels": [
            {
                "level_name": "Easy",
                "target_min": 5,
                "target_max": 10,
                "addends": [
                    {"min_value": 1, "max_value": 5},
                    {"min_value": 1, "max_value": 5}
                ],
                "time_limit": None,
                "hints_available": True
            }
        ],
        "starting_level": "Easy",
        "public": True,
        "feedback_sensitivity": 1.0,
        "progression_criteria": {}
    }
    
    create_response = client.post(
        "/game-configurations/",
        json=sample_config,
        headers=auth_headers
    )
    
    config_id = create_response.json()["id"]
    
    # Now update it
    updated_config = create_response.json()
    updated_config["title"] = "Updated Test Game"
    
    update_response = client.put(
        f"/game-configurations/{config_id}",
        json=updated_config,
        headers=auth_headers
    )
    
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Test Game"

# Test Game Session
def test_create_game_session(mock_firebase_auth, auth_headers):
    # First create a configuration
    sample_config = {
        "title": "Test Game",
        "description": "A test game configuration",
        "difficulty_levels": [
            {
                "level_name": "Easy",
                "target_min": 5,
                "target_max": 10,
                "addends": [
                    {"min_value": 1, "max_value": 5},
                    {"min_value": 1, "max_value": 5}
                ],
                "time_limit": None,
                "hints_available": True
            }
        ],
        "starting_level": "Easy",
        "public": True,
        "feedback_sensitivity": 1.0,
        "progression_criteria": {}
    }
    
    create_response = client.post(
        "/game-configurations/",
        json=sample_config,
        headers=auth_headers
    )
    
    config_id = create_response.json()["id"]
    
    # Create a game session
    session_response = client.post(
        f"/game-sessions/?config_id={config_id}",
        headers=auth_headers
    )
    
    assert session_response.status_code == 200
    session_data = session_response.json()
    assert "id" in session_data
    assert session_data["configuration_id"] == config_id
    assert session_data["user_id"] == "test-user-123"
    assert session_data["difficulty_level"] == "Easy"
    assert "target_number" in session_data
    assert not session_data["completed"]

def test_record_attempt(mock_firebase_auth, auth_headers):
    # First create a configuration
    sample_config = {
        "title": "Test Game",
        "description": "A test game configuration",
        "difficulty_levels": [
            {
                "level_name": "Easy",
                "target_min": 5,
                "target_max": 10,
                "addends": [
                    {"min_value": 1, "max_value": 5},
                    {"min_value": 1, "max_value": 5}
                ],
                "time_limit": None,
                "hints_available": True
            }
        ],
        "starting_level": "Easy",
        "public": True,
        "feedback_sensitivity": 1.0,
        "progression_criteria": {}
    }
    
    create_response = client.post(
        "/game-configurations/",
        json=sample_config,
        headers=auth_headers
    )
    
    config_id = create_response.json()["id"]
    
    # Create a game session
    session_response = client.post(
        f"/game-sessions/?config_id={config_id}",
        headers=auth_headers
    )
    
    session_id = session_response.json()["id"]
    target_number = session_response.json()["target_number"]
    
    # Record an attempt (correct answer)
    if target_number % 2 == 0:
        addends = [target_number // 2, target_number // 2]
    else:
        addends = [target_number // 2, target_number // 2 + 1]
    
    attempt_response = client.post(
        f"/game-sessions/{session_id}/attempt",
        json={
            "addends": addends,
            "time_taken": 5.2
        },
        headers=auth_headers
    )
    
    assert attempt_response.status_code == 200
    attempt_data = attempt_response.json()
    assert attempt_data["session_id"] == session