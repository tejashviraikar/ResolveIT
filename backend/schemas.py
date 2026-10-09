from pydantic import BaseModel, Field, EmailStr


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=100)

class IssueCreate(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "MEDIUM"


class IssueAssign(BaseModel):
    assigned_to: int



class IssueStatusUpdate(BaseModel):
    status: str

VALID_CATEGORIES = {
    "Hardware",
    "Software",
    "Network",
    "Account/Login",
    "Database",
    "Other"
}

VALID_PRIORITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
}

VALID_STATUSES = {
    "OPEN",
    "ASSIGNED",
    "IN PROGRESS",
    "RESOLVED",
    "CLOSED"
}

class CommentCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=1000)