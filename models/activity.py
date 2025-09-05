# models/activity.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class ActivityType(Enum):
    QUERY = "query"
    LOGIN = "login"
    LOGOUT = "logout"
    DOCUMENT_VIEW = "document_view"
    RESPONSE_RATING = "response_rating"

@dataclass
class StudentActivity:
    """Comprehensive student activity logging"""
    id: str
    student_id: str
    session_id: str
    activity_type: ActivityType
    timestamp: str
    
    # Query-specific fields
    query_text: Optional[str] = None
    response_text: Optional[str] = None
    sources_used: Optional[List[str]] = None
    response_time_ms: Optional[int] = None
    grounding_confidence: Optional[float] = None
    
    # Topic analysis
    detected_topics: Optional[List[str]] = None
    difficulty_level: Optional[str] = None  # "basic", "intermediate", "advanced"
    
    # Engagement metrics
    session_duration_sec: Optional[int] = None
    follow_up_questions: Optional[int] = None
    satisfaction_rating: Optional[int] = None  # 1-5 scale
    
    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LearningSession:
    """Represents a complete learning session"""
    id: str
    student_id: str
    start_time: str
    end_time: Optional[str] = None
    total_queries: int = 0
    unique_topics: List[str] = None
    average_confidence: Optional[float] = None
    session_quality_score: Optional[float] = None

@dataclass
class ProgressMetrics:
    """Student progress analytics"""
    student_id: str
    period_start: str
    period_end: str
    
    # Query metrics
    total_queries: int
    unique_topics_explored: int
    average_session_duration: float
    
    # Learning patterns
    most_active_hours: List[int]  # Hours of day (0-23)
    preferred_topics: List[str]
    difficulty_progression: List[str]  # Track if moving to harder topics
    
    # Engagement metrics
    sessions_per_week: float
    average_response_satisfaction: float
    knowledge_retention_score: Optional[float] = None