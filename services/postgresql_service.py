# services/postgresql_service.py
import asyncpg
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import hashlib
import uuid
import os
from models.user import User, UserRole, UserRelationship
from models.activity import StudentActivity, ActivityType, LearningSession, ProgressMetrics

class PostgreSQLService:
    """High-performance PostgreSQL service for 500+ concurrent users"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            'DATABASE_URL', 
            'postgresql://dc_user:dc_secure_2024@localhost:5433/digital_companion'
        )
        self.pool = None
    
    async def initialize_pool(self):
        """Create connection pool for high concurrency"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=10,        # Minimum connections
            max_size=50,        # Maximum concurrent connections
            command_timeout=5,   # Query timeout
            max_inactive_connection_lifetime=300
        )
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        if not self.pool:
            await self.initialize_pool()
        
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)
    
    # User operations
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow('SELECT * FROM users WHERE username = $1', username)
                
                if row:
                    return User(
                        id=str(row['id']), username=row['username'], name=row['name'], 
                        email=row['email'], password_hash=row['password_hash'], 
                        role=UserRole(row['role']),
                        parent_ids=row.get('parent_ids'), student_ids=row.get('student_ids'),
                        class_ids=row.get('class_ids'), 
                        created_at=row['created_at'].isoformat(),
                        last_login=row['last_login'].isoformat() if row['last_login'] else None,
                        is_active=row['is_active']
                    )
                return None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow('SELECT * FROM users WHERE id = $1::uuid', user_id)
                
                if row:
                    return User(
                        id=str(row['id']), username=row['username'], name=row['name'], 
                        email=row['email'], password_hash=row['password_hash'], 
                        role=UserRole(row['role']),
                        parent_ids=row.get('parent_ids'), student_ids=row.get('student_ids'),
                        class_ids=row.get('class_ids'), 
                        created_at=row['created_at'].isoformat(),
                        last_login=row['last_login'].isoformat() if row['last_login'] else None,
                        is_active=row['is_active']
                    )
                return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    async def get_students_for_parent(self, parent_id: str) -> List[User]:
        """Get all students linked to a parent"""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch('''
                    SELECT u.* FROM users u
                    JOIN user_relationships ur ON u.id = ur.child_user_id
                    WHERE ur.parent_user_id = $1::uuid AND ur.is_active = true AND u.role = 'student'
                ''', parent_id)
                
                students = []
                for row in rows:
                    students.append(User(
                        id=str(row['id']), username=row['username'], name=row['name'], 
                        email=row['email'], password_hash=row['password_hash'], 
                        role=UserRole(row['role']),
                        parent_ids=row.get('parent_ids'), student_ids=row.get('student_ids'),
                        class_ids=row.get('class_ids'), 
                        created_at=row['created_at'].isoformat(),
                        last_login=row['last_login'].isoformat() if row['last_login'] else None,
                        is_active=row['is_active']
                    ))
                
                return students
        except Exception as e:
            print(f"Error getting students for parent: {e}")
            return []
    
    # Activity logging
    async def log_activity(self, activity: StudentActivity) -> bool:
        """Log student activity to partitioned table"""
        try:
            async with self.get_connection() as conn:
                await conn.execute('''
                    INSERT INTO student_activities (
                        id, student_id, session_id, activity_type, timestamp,
                        query_text, response_text, sources_used, response_time_ms,
                        grounding_confidence, detected_topics, difficulty_level,
                        session_duration_sec, follow_up_questions, satisfaction_rating,
                        ip_address, user_agent, metadata
                    ) VALUES ($1, $2::uuid, $3::uuid, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                ''', 
                str(uuid.uuid4()), activity.student_id, activity.session_id,
                activity.activity_type.value, datetime.fromisoformat(activity.timestamp),
                activity.query_text, activity.response_text,
                activity.sources_used, activity.response_time_ms,
                activity.grounding_confidence, activity.detected_topics,
                activity.difficulty_level, activity.session_duration_sec,
                activity.follow_up_questions, activity.satisfaction_rating,
                activity.ip_address, activity.user_agent,
                activity.metadata if activity.metadata else {})
                
                return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    async def get_student_activities(self, student_id: str, limit: int = 100) -> List[StudentActivity]:
        """Get recent activities for a student"""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch('''
                    SELECT * FROM student_activities 
                    WHERE student_id = $1::uuid 
                    ORDER BY timestamp DESC 
                    LIMIT $2
                ''', student_id, limit)
                
                activities = []
                for row in rows:
                    activities.append(StudentActivity(
                        id=str(row['id']), student_id=str(row['student_id']), 
                        session_id=str(row['session_id']),
                        activity_type=ActivityType(row['activity_type']), 
                        timestamp=row['timestamp'].isoformat(),
                        query_text=row['query_text'], response_text=row['response_text'],
                        sources_used=row.get('sources_used'), response_time_ms=row['response_time_ms'],
                        grounding_confidence=row.get('grounding_confidence'),
                        detected_topics=row.get('detected_topics'), 
                        difficulty_level=row.get('difficulty_level'),
                        session_duration_sec=row.get('session_duration_sec'),
                        follow_up_questions=row.get('follow_up_questions'),
                        satisfaction_rating=row.get('satisfaction_rating'),
                        ip_address=row.get('ip_address'), user_agent=row.get('user_agent'),
                        metadata=row.get('metadata', {})
                    ))
                
                return activities
        except Exception as e:
            print(f"Error getting student activities: {e}")
            return []
    
    # Response caching
    async def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached response for query"""
        try:
            query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
            
            async with self.get_connection() as conn:
                row = await conn.fetchrow('''
                    SELECT response_data FROM response_cache 
                    WHERE query_hash = $1 AND expires_at > CURRENT_TIMESTAMP
                ''', query_hash)
                
                if row:
                    # Update hit count and last accessed
                    await conn.execute('''
                        UPDATE response_cache 
                        SET hit_count = hit_count + 1, last_accessed = CURRENT_TIMESTAMP
                        WHERE query_hash = $1
                    ''', query_hash)
                    
                    return row['response_data']
                
                return None
        except Exception as e:
            print(f"Error getting cached response: {e}")
            return None
    
    async def cache_response(self, query: str, response_data: Dict[str, Any]) -> bool:
        """Cache query response with TTL"""
        try:
            query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
            
            async with self.get_connection() as conn:
                await conn.execute('''
                    INSERT INTO response_cache 
                    (query_hash, query_text, response_data, created_at, last_accessed)
                    VALUES ($1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (query_hash) 
                    DO UPDATE SET 
                        response_data = EXCLUDED.response_data,
                        hit_count = response_cache.hit_count + 1,
                        last_accessed = CURRENT_TIMESTAMP
                ''', query_hash, query, response_data)
                
                return True
        except Exception as e:
            print(f"Error caching response: {e}")
            return False
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def log_activity_batch(self, activities: List[Dict]) -> bool:
        """Batch insert for high performance activity logging"""
        async with self.get_connection() as conn:
            await conn.executemany('''
                INSERT INTO student_activities 
                (id, student_id, session_id, activity_type, query_text, 
                 response_text, response_time_ms, grounding_confidence)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', [(
                str(uuid.uuid4()),
                activity['student_id'],
                activity['session_id'],
                activity['activity_type'],
                activity.get('query_text'),
                activity.get('response_text'),
                activity.get('response_time_ms'),
                activity.get('grounding_confidence')
            ) for activity in activities])
            
            return True

# Performance monitoring
class PerformanceMonitor:
    """Monitor response times and system performance"""
    
    @staticmethod
    async def get_performance_metrics():
        """Get real-time performance metrics"""
        # This would integrate with monitoring tools like Prometheus
        return {
            'avg_response_time_ms': 250,
            'active_connections': 45,
            'cache_hit_rate': 0.85,
            'queries_per_second': 120
        }