from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from mysql.connector import IntegrityError

from backend.database import get_connection

from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

from backend.schemas import (
    UserRegister,
    UserLogin,
    IssueCreate,
    IssueAssign,
    IssueStatusUpdate,
    CommentCreate,
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    VALID_STATUSES
)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ResolveIT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# =========================
# Authentication
# =========================

def get_current_user(token: str = Depends(oauth2_scheme)):

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload


# =========================
# Role-Based Authorization
# =========================

def require_support(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "SUPPORT":
        raise HTTPException(
            status_code=403,
            detail="Support staff access required"
        )

    return current_user


# =========================
# Home
# =========================

@app.get("/")
def home():

    return {
        "message": "Welcome to ResolveIT",
        "status": "API is running"
    }


# =========================
# Test Database
# =========================

@app.get("/test-db")
def test_database():

    connection = get_connection()

    if connection.is_connected():

        connection.close()

        return {
            "message": "MySQL connection successful"
        }

    return {
        "message": "MySQL connection failed"
    }


# =========================
# Register
# =========================

@app.post("/register")
def register_user(user: UserRegister):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO users
        (name, email, password, role)
        VALUES (%s, %s, %s, %s)
    """

    hashed_password = hash_password(user.password)

    values = (
        user.name,
        user.email,
        hashed_password,
        "EMPLOYEE"
    )

    try:
        cursor.execute(query, values)
        connection.commit()
    except IntegrityError:
        connection.rollback()
        cursor.close()
        connection.close()
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    
    cursor.close()
    connection.close()

    return {
        "message": "User registered successfully"
    }


# =========================
# Login
# =========================

@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT user_id, name, email, password, role
        FROM users
        WHERE email = %s
    """

    cursor.execute(query, (form_data.username,))
    existing_user = cursor.fetchone()

    cursor.close()
    connection.close()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        existing_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        existing_user["user_id"],
        existing_user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# Create Issue
# =========================

@app.post("/issues")
def create_issue(
    issue: IssueCreate,
    current_user: dict = Depends(get_current_user)
):

    # Validate category
    if issue.category not in VALID_CATEGORIES:

        raise HTTPException(
            status_code=400,
            detail="Invalid category"
        )

    # Validate priority
    if issue.priority not in VALID_PRIORITIES:

        raise HTTPException(
            status_code=400,
            detail="Invalid priority"
        )

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO issues
        (title, description, category, priority, status, created_by)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        issue.title,
        issue.description,
        issue.category,
        issue.priority,
        "OPEN",
        current_user["user_id"]
    )

    cursor.execute(query, values)
    connection.commit()

    issue_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Issue created successfully",
        "issue_id": issue_id
    }


# =========================
# Get Issues
# =========================

@app.get("/issues")
def get_issues(
    current_user: dict = Depends(get_current_user)
):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if current_user["role"] == "SUPPORT":

        query = """
            SELECT issue_id, title, description, category,
                   priority, status, created_by, assigned_to,
                   created_at, updated_at
            FROM issues
            ORDER BY created_at DESC
        """

        cursor.execute(query)

    else:

        query = """
            SELECT issue_id, title, description, category,
                   priority, status, created_by, assigned_to,
                   created_at, updated_at
            FROM issues
            WHERE created_by = %s
            ORDER BY created_at DESC
        """

        cursor.execute(
            query,
            (current_user["user_id"],)
        )

    issues = cursor.fetchall()

    cursor.close()
    connection.close()

    return {
        "issues": issues
    }

# =========================
# Search Issues
# =========================

@app.get("/issues/search")
def search_issues(
    status: str = None,
    priority: str = None,
    category: str = None,
    search: str = None,
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT issue_id, title, description, category,
               priority, status, created_by, assigned_to,
               created_at, updated_at
        FROM issues
        WHERE 1=1
    """

    values = []

    # Employee can only search their own issues
    if current_user["role"] == "EMPLOYEE":
        query += " AND created_by = %s"
        values.append(current_user["user_id"])

    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Invalid status"
            )

        query += " AND status = %s"
        values.append(status)

    if priority:
        if priority not in VALID_PRIORITIES:
            raise HTTPException(
                status_code=400,
                detail="Invalid priority"
            )

        query += " AND priority = %s"
        values.append(priority)

    if category:
        if category not in VALID_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail="Invalid category"
            )

        query += " AND category = %s"
        values.append(category)

    if search:
        query += """
            AND (
                title LIKE %s
                OR description LIKE %s
            )
        """

        search_value = f"%{search}%"
        values.append(search_value)
        values.append(search_value)

    query += " ORDER BY created_at DESC"

    cursor.execute(
        query,
        tuple(values)
    )

    issues = cursor.fetchall()

    cursor.close()
    connection.close()

    return {
        "issues": issues
    }

# =========================
# Get Single Issue
# =========================

@app.get("/issues/{issue_id}")
def get_issue(
    issue_id: int,
    current_user: dict = Depends(get_current_user)
):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT issue_id, title, description, category,
               priority, status, created_by, assigned_to,
               created_at, updated_at
        FROM issues
        WHERE issue_id = %s
    """

    cursor.execute(
        query,
        (issue_id,)
    )

    issue = cursor.fetchone()

    cursor.close()
    connection.close()

    if issue is None:

        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    # Employee can access only their own issue
    if (
        current_user["role"] == "EMPLOYEE"
        and issue["created_by"] != current_user["user_id"]
    ):

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view this issue"
        )

    return issue


# =========================
# Assign Issue
# Support Only
# =========================

@app.put("/issues/{issue_id}/assign")
def assign_issue(
    issue_id: int,
    assignment: IssueAssign,
    current_user: dict = Depends(require_support)
):

    connection = get_connection()
    cursor = connection.cursor()

    # Check issue
    cursor.execute(
        "SELECT issue_id FROM issues WHERE issue_id = %s",
        (issue_id,)
    )

    issue = cursor.fetchone()

    if issue is None:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    # Check assigned user
    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = %s",
        (assignment.assigned_to,)
    )

    user = cursor.fetchone()

    if user is None:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    query = """
        UPDATE issues
        SET assigned_to = %s,
            status = 'ASSIGNED'
        WHERE issue_id = %s
    """

    cursor.execute(
        query,
        (
            assignment.assigned_to,
            issue_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Issue assigned successfully",
        "issue_id": issue_id,
        "assigned_to": assignment.assigned_to,
        "status": "ASSIGNED"
    }


# =========================
# Update Issue Status
# Support Only
# =========================

@app.put("/issues/{issue_id}/status")
def update_issue_status(
    issue_id: int,
    status_update: IssueStatusUpdate,
    current_user: dict = Depends(require_support)
):

    # Validate status
    if status_update.status not in VALID_STATUSES:

        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    connection = get_connection()
    cursor = connection.cursor()

    # Check issue
    cursor.execute(
        "SELECT issue_id FROM issues WHERE issue_id = %s",
        (issue_id,)
    )

    issue = cursor.fetchone()

    if issue is None:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    query = """
        UPDATE issues
        SET status = %s
        WHERE issue_id = %s
    """

    cursor.execute(
        query,
        (
            status_update.status,
            issue_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Issue status updated successfully",
        "issue_id": issue_id,
        "status": status_update.status
    }

@app.put("/issues/{issue_id}/close")
def close_issue(
    issue_id: int,
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Get the issue
    query = """
        SELECT issue_id, created_by, status
        FROM issues
        WHERE issue_id = %s
    """

    cursor.execute(query, (issue_id,))
    issue = cursor.fetchone()

    if issue is None:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    # Only the employee who created the issue can close it
    if current_user["role"] == "EMPLOYEE":
        if issue["created_by"] != current_user["user_id"]:
            cursor.close()
            connection.close()

            raise HTTPException(
                status_code=403,
                detail="You are not allowed to close this issue"
            )

    # Issue must be resolved first
    if issue["status"] != "RESOLVED":
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Only resolved issues can be closed"
        )

    update_query = """
        UPDATE issues
        SET status = 'CLOSED'
        WHERE issue_id = %s
    """

    cursor.execute(update_query, (issue_id,))
    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Issue closed successfully"
    }

# =========================
# Add Comment
# =========================

@app.post("/issues/{issue_id}/comments")
def add_comment(
    issue_id: int,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Check issue
    cursor.execute(
        """
        SELECT issue_id, created_by
        FROM issues
        WHERE issue_id = %s
        """,
        (issue_id,)
    )

    issue = cursor.fetchone()

    if issue is None:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    # Employee can comment only on own issue
    if (
        current_user["role"] == "EMPLOYEE"
        and issue["created_by"] != current_user["user_id"]
    ):

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to comment on this issue"
        )

    query = """
        INSERT INTO comments
        (issue_id, user_id, comment)
        VALUES (%s, %s, %s)
    """

    values = (
        issue_id,
        current_user["user_id"],
        comment_data.comment
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    comment_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Comment added successfully",
        "comment_id": comment_id
    }


# =========================
# Get Comments
# =========================

@app.get("/issues/{issue_id}/comments")
def get_comments(
    issue_id: int,
    current_user: dict = Depends(get_current_user)
):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Check issue
    cursor.execute(
        """
        SELECT issue_id, created_by
        FROM issues
        WHERE issue_id = %s
        """,
        (issue_id,)
    )

    issue = cursor.fetchone()

    if issue is None:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    # Employee can view comments only on own issue
    if (
        current_user["role"] == "EMPLOYEE"
        and issue["created_by"] != current_user["user_id"]
    ):

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view these comments"
        )

    query = """
        SELECT comments.comment_id,
               comments.comment,
               comments.created_at,
               users.user_id,
               users.name,
               users.role
        FROM comments
        JOIN users
            ON comments.user_id = users.user_id
        WHERE comments.issue_id = %s
        ORDER BY comments.created_at ASC
    """

    cursor.execute(
        query,
        (issue_id,)
    )

    comments = cursor.fetchall()

    cursor.close()
    connection.close()

    return {
        "issue_id": issue_id,
        "comments": comments
    }



# =========================
# Dashboard
# =========================

@app.get("/dashboard")
def get_dashboard(
    current_user: dict = Depends(require_support)
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            COUNT(*) AS total_issues,
            SUM(status = 'OPEN') AS open_issues,
            SUM(status = 'ASSIGNED') AS assigned_issues,
            SUM(status = 'IN PROGRESS') AS in_progress_issues,
            SUM(status = 'RESOLVED') AS resolved_issues,
            SUM(status = 'CLOSED') AS closed_issues,
            SUM(priority IN ('HIGH', 'CRITICAL'))
                AS high_priority_issues
        FROM issues
    """

    cursor.execute(query)

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result