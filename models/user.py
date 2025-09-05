# models/user.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"

@dataclass
class User:
    """User model with role-based permissions"""
    id: str
    username: str
    name: str
    email: str
    password_hash: str
    role: UserRole
    parent_ids: Optional[List[str]] = None  # For students - list of parent IDs
    student_ids: Optional[List[str]] = None  # For parents - list of student IDs
    class_ids: Optional[List[str]] = None   # For teachers - list of class IDs
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    is_active: bool = True

    @property
    def can_upload_documents(self) -> bool:
        """Only admin can upload documents"""
        return self.role == UserRole.ADMIN

    @property
    def can_view_analytics(self) -> bool:
        """Admin and teachers can view analytics"""
        return self.role in [UserRole.ADMIN, UserRole.TEACHER]

    @property
    def can_view_student_progress(self) -> bool:
        """Parents and teachers can view student progress"""
        return self.role in [UserRole.PARENT, UserRole.TEACHER]

@dataclass
class UserRelationship:
    """Represents parent-student or teacher-student relationships"""
    id: str
    parent_user_id: str
    child_user_id: str
    relationship_type: str  # "parent", "teacher", "guardian"
    created_at: str
    is_active: bool = True