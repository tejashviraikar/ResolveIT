# ResolveIT – IT Issue Tracking & Resolution System

## Project Overview

ResolveIT is a web-based IT issue tracking system that helps employees report technical problems and allows support staff to manage, assign, and resolve them.

The system provides a centralized platform for tracking issue status, communicating through comments, and monitoring support activities.

## Features

- User registration and login
- Password hashing and JWT-based authentication
- Role-based access for Employees and Support Staff
- Create and view IT issues
- Issue assignment to support staff
- Issue status management
- Comments and issue discussion
- Search and filter issues by status, priority, category, and keywords
- Support dashboard with issue statistics
- Automated API testing with Pytest

## Technology Stack

**Frontend**

- HTML
- CSS
- JavaScript

**Backend**

- Python
- FastAPI
- REST APIs
- JWT authentication
- bcrypt password hashing

**Database**

- MySQL

**Testing and Tools**

- Pytest
- Git and GitHub
- Visual Studio Code

## System Workflow

1. An employee registers and logs in.
2. The employee creates an IT issue.
3. Support staff views and assigns the issue.
4. Support staff updates its status and adds comments.
5. The employee can track progress and close the issue after resolution.

## Project Structure

```text
ResolveIT/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   └── security.py
├── frontend/
│   ├── index.html
│   ├── register.html
│   ├── employee-dashboard.html
│   ├── support-dashboard.html
│   ├── issue.html
│   ├── css/
│   │   └── style.css
│   └── js/
├── tests/
│   └── test_api.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ResolveIT
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file using `.env.example` as a reference. Set your local MySQL credentials, database name, and a secure JWT secret.

Never commit your real `.env` file or passwords to GitHub.

### 5. Create the database

Create a MySQL database named `resolveit_db` and execute the SQL statements for the `users`, `issues`, and `comments` tables.

### 6. Start the backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

Open the API documentation at:

http://127.0.0.1:8000/docs

### 7. Start the frontend

Open another terminal:

```bash
cd frontend
python -m http.server 5500
```

Open:

http://127.0.0.1:5500/index.html

## Testing

Run the automated test suite from the project root:

```bash
pytest -v
```

The current test suite contains 14 passing tests.

## Learning Outcomes

- REST API development with FastAPI
- Relational database design and SQL
- Authentication and role-based authorization
- Frontend-to-backend integration
- CRUD operations and issue workflow management
- Automated API testing

## Future Improvements

- Email notifications for issue updates
- Pagination for large issue lists
- Audit logs for status changes and assignments
- More comprehensive integration and security tests

## Author

Computer Engineering Student
