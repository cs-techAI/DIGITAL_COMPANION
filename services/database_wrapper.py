# services/database_wrapper.py
"""
Synchronous wrapper for PostgreSQL service to maintain compatibility with existing Streamlit code
"""
import asyncio
from typing import List, Optional, Dict, Any
from services.postgresql_service import PostgreSQLService
from models.user import User, UserRole, UserRelationship
from models.activity import StudentActivity, ActivityType, LearningSession, ProgressMetrics

class DatabaseWrapper:
    """Synchronous wrapper around PostgreSQL service for backward compatibility"""
    
    def __init__(self):
        self.pg_service = PostgreSQLService()
        self.loop = None
        self._ensure_loop()
    
    def _ensure_loop(self):
        """Ensure we have an event loop"""
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        if not self.loop.is_running():
            return self.loop.run_until_complete(coro)
        else:
            # If loop is already running (in Streamlit), create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
    
    # User operations (sync interface)
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (sync)"""
        return self._run_async(self.pg_service.get_user_by_username(username))
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID (sync)"""
        return self._run_async(self.pg_service.get_user_by_id(user_id))
    
    def get_students_for_parent(self, parent_id: str) -> List[User]:
        """Get students for parent (sync)"""
        return self._run_async(self.pg_service.get_students_for_parent(parent_id))
    
    # Activity operations (sync interface)
    def log_activity(self, activity: StudentActivity) -> bool:
        """Log activity (sync)"""
        return self._run_async(self.pg_service.log_activity(activity))
    
    def get_student_activities(self, student_id: str, limit: int = 100) -> List[StudentActivity]:
        """Get student activities (sync)"""
        return self._run_async(self.pg_service.get_student_activities(student_id, limit))
    
    # Caching operations (sync interface)
    def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached response (sync)"""
        return self._run_async(self.pg_service.get_cached_response(query))
    
    def cache_response(self, query: str, response_data: Dict[str, Any]) -> bool:
        """Cache response (sync)"""
        return self._run_async(self.pg_service.cache_response(query, response_data))
    
    # Compatibility methods for existing code
    def create_user(self, user: User) -> bool:
        """Create user - not implemented for production use"""
        print("⚠️ User creation not implemented in PostgreSQL wrapper")
        return False
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'loop') and self.loop:
            try:
                self._run_async(self.pg_service.close())
            except:
                pass

# Global database service instance
database_service = DatabaseWrapper()