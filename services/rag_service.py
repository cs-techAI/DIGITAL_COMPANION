# services/rag_service.py
import streamlit as st
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.user import User, UserRole
from services.activity_service import ActivityService

class RAGService:
    """Service for RAG operations with activity logging and caching"""
    
    def __init__(self, db_service, activity_service: ActivityService):
        self.db = db_service
        self.activity_service = activity_service
    
    def generate_response_with_logging(self, query: str, current_user: User, 
                                     session_id: str, chatbot, vector_store) -> Dict[str, Any]:
        """Generate response with comprehensive logging and caching"""
        start_time = time.time()
        
        # Check cache first for performance
        cached_response = self.db.get_cached_response(query)
        if cached_response:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Still log the query for analytics
            if current_user.role == UserRole.STUDENT:
                # Extract filenames from cached sources (they might be full objects or strings)
                cached_sources = cached_response.get('sources', [])
                if cached_sources and isinstance(cached_sources[0], dict):
                    # Full search results
                    source_files = [source.get("metadata", {}).get("source_file", "Unknown") 
                                   for source in cached_sources]
                else:
                    # Already just filenames
                    source_files = cached_sources
                
                self.activity_service.log_query_activity(
                    student_id=current_user.id,
                    session_id=session_id,
                    query=query,
                    response=cached_response['response'],
                    sources=source_files,
                    response_time_ms=response_time_ms,
                    grounding_confidence=cached_response.get('grounding_confidence')
                )
            
            return {
                'response': cached_response['response'],
                'grounding_result': cached_response.get('grounding_result'),
                'sources': cached_response.get('sources', []),
                'is_cached': True,
                'response_time_ms': response_time_ms
            }
        
        # Generate new response
        context = ""
        sources = []
        
        if vector_store and st.session_state.documents:
            search_results = vector_store.search(query, k=5, relevance_threshold=0.3)
            if search_results:
                context = "\\n\\n".join([result["content"] for result in search_results])
                sources = search_results  # Keep full search results instead of just filenames
        
        # Generate response using existing chatbot
        response_data = chatbot.generate_response(query, context)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Cache the response for future use (store full sources for UI)
        cache_data = {
            'response': response_data['response'],
            'grounding_result': response_data.get('grounding_result'),
            'sources': sources,  # Full search results for UI display
            'grounding_confidence': response_data.get('grounding_result', {}).get('confidence')
        }
        self.db.cache_response(query, cache_data)
        
        # Log activity for students
        if current_user.role == UserRole.STUDENT:
            # Extract just filenames for activity logging
            source_files = [source.get("metadata", {}).get("source_file", "Unknown") 
                           for source in sources] if sources else []
            
            self.activity_service.log_query_activity(
                student_id=current_user.id,
                session_id=session_id,
                query=query,
                response=response_data['response'],
                sources=source_files,
                response_time_ms=response_time_ms,
                grounding_confidence=response_data.get('grounding_result', {}).get('confidence')
            )
        
        return {
            'response': response_data['response'],
            'grounding_result': response_data.get('grounding_result'),
            'sources': sources,
            'is_cached': False,
            'response_time_ms': response_time_ms,
            'is_fallback': response_data.get('is_fallback', False)
        }
    
    def get_relevant_context(self, query: str, vector_store, k: int = 5) -> tuple[str, List[Dict]]:
        """Get relevant context from vector store"""
        context = ""
        sources = []
        
        if vector_store and st.session_state.documents:
            search_results = vector_store.search(query, k=k, relevance_threshold=0.3)
            if search_results:
                context = "\\n\\n".join([result["content"] for result in search_results])
                sources = search_results
        
        return context, sources
    
    def clear_user_cache(self, user_id: str) -> bool:
        """Clear cached responses (admin only)"""
        # This would be implemented to clear specific user caches
        return True