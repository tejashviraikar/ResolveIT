import os
from dotenv import load_dotenv

load_dotenv()

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "API is running"


def test_create_issue_requires_authentication():
    response = client.post(
        "/issues",
        json={
            "title": "Test issue",
            "description": "This is a test issue",
            "category": "Software",
            "priority": "MEDIUM"
        }
    )

    assert response.status_code == 401


def test_get_issues_requires_authentication():
    response = client.get("/issues")

    assert response.status_code == 401


def test_search_requires_authentication():
    response = client.get("/issues/search?status=OPEN")

    assert response.status_code == 401


def test_dashboard_requires_authentication():
    response = client.get("/dashboard")

    assert response.status_code == 401


def test_employee_cannot_assign_issue():
    response = client.put(
        "/issues/1/assign",
        json={
            "assigned_to": 2
        }
    )

    assert response.status_code == 401


def test_employee_cannot_change_issue_status():
    response = client.put(
        "/issues/1/status",
        json={
            "status": "RESOLVED"
        }
    )

    assert response.status_code == 401

def test_employee_cannot_assign_issue():
    login_response = client.post(
        "/login",
        data={
            "username": "secure@gmail.com",
            "password": "123456"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.put(
        "/issues/1/assign",
        json={
            "assigned_to": 2
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403

def test_support_can_assign_issue():
    login_response = client.post(
        "/login",
        data={
            "username": "support2@gmail.com",
            "password": "789456"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.put(
        "/issues/1/assign",
        json={
            "assigned_to": 2
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

def test_support_can_change_issue_status():
    login_response = client.post(
        "/login",
        data={
            "username": "support2@gmail.com",
            "password": "789456"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.put(
        "/issues/1/status",
        json={
            "status": "IN PROGRESS"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

def test_invalid_issue_category():
    login_response = client.post(
        "/login",
        data={
            "username": os.getenv("TEST_EMPLOYEE_EMAIL"),
            "password": os.getenv("TEST_EMPLOYEE_PASSWORD")
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/issues",
        json={
            "title": "Invalid category test",
            "description": "Testing category validation",
            "category": "InvalidCategory",
            "priority": "MEDIUM"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid category"

def test_duplicate_email_registration():
    response = client.post(
        "/register",
        json={
            "name": "Duplicate Test User",
            "email": "secure@gmail.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code in [400, 409]

def test_invalid_email_registration():
    response = client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 422

def test_short_password_registration():
    response = client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "validtest@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 422

def test_register_missing_required_fields():
    response = client.post(
        "/register",
        json={}
    )

    assert response.status_code == 422