# ui/components.py
import streamlit as st
from typing import Dict, Any, List
from models.user import User, UserRole
from services.document_service import DocumentService

def apply_role_theme(role: str):
    """Apply custom CSS based on user role"""
    themes = {
        'admin': {
            'primary': '#D32F2F',
            'secondary': '#F44336',
            'accent': '#FFEBEE',
            'text': '#B71C1C'
        },
        'student': {
            'primary': '#1E88E5',
            'secondary': '#42A5F5',
            'accent': '#E3F2FD',
            'text': '#0D47A1'
        },
        'teacher': {
            'primary': '#43A047',
            'secondary': '#66BB6A',
            'accent': '#E8F5E8',
            'text': '#1B5E20'
        },
        'parent': {
            'primary': '#FB8C00',
            'secondary': '#FFB74D',
            'accent': '#FFF3E0',
            'text': '#E65100'
        }
    }

    if role in themes:
        theme = themes[role]
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, {theme['accent']} 0%, #ffffff 100%);
        }}
        .stButton > button {{
            background: {theme['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        .stButton > button:hover {{
            background: {theme['secondary']};
        }}
        .stSelectbox > div > div {{
            background: {theme['accent']};
        }}
        .role-header {{
            background: {theme['primary']};
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
        }}
        .metric-card {{
            background: {theme['accent']};
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid {theme['primary']};
            margin: 0.5rem 0;
        }}
        .logout-btn {{
            background: #dc3545 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
        }}
        .logout-btn:hover {{
            background: #c82333 !important;
        }}
        </style>
        """, unsafe_allow_html=True)

def render_role_header(role: str, name: str):
    """Render clean AERO role-specific header"""
    role_config = {
        'admin': {'emoji': '🔧', 'title': 'System Administration'},
        'student': {'emoji': '🚀', 'title': 'Learning Hub'}, 
        'teacher': {'emoji': '📊', 'title': 'Analytics Dashboard'}, 
        'parent': {'emoji': '👨‍👩‍👧‍👦', 'title': 'Student Progress'}
    }
    
    config = role_config.get(role, {'emoji': '🚀', 'title': 'AERO Assistant'})
    st.markdown(f'<div class="role-header">{config["emoji"]} AERO - {config["title"]} | {name}</div>', 
                unsafe_allow_html=True)

def render_document_upload_section(current_user: User, document_service: DocumentService):
    """Render document upload section with role-based access"""
    st.sidebar.header("📁 Knowledge Base Management")
    
    # Check if user is admin
    if current_user and current_user.role == UserRole.ADMIN:
        st.sidebar.success("🔧 **Admin Access** - Document Upload Enabled")
        
        # File upload tabs for admin
        tab1, tab2, tab3 = st.sidebar.tabs(["📄 Documents", "🎥 Videos", "🌐 YouTube"])
        
        with tab1:
            uploaded_files = st.file_uploader(
                "Upload Documents (Admin Only)",
                accept_multiple_files=True,
                type=['pdf', 'txt'],
                help="Upload PDF or TXT files to shared knowledge base"
            )

            if uploaded_files and st.button("🔄 Process Documents", key="process_docs"):
                document_service.process_documents_admin(uploaded_files, current_user, st.session_state.vector_store)

        with tab2:
            uploaded_videos = st.file_uploader(
                "Upload Videos (Admin Only)",
                accept_multiple_files=True,
                type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
                help="Upload video files for transcription"
            )

            if uploaded_videos and st.button("🎬 Process Videos", key="process_videos"):
                document_service.process_videos_admin(uploaded_videos, current_user, st.session_state.vector_store)

        with tab3:
            youtube_url = st.text_input(
                "YouTube URL (Admin Only)",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Enter YouTube video URL"
            )

            if youtube_url and st.button("📺 Process YouTube", key="process_youtube"):
                document_service.process_youtube_admin(youtube_url, current_user, st.session_state.vector_store)
    else:
        # Non-admin users see read-only info
        role = current_user.role.value if current_user else 'student'
        st.sidebar.info(f"📚 **{role.title()} Access** - Query Only")
        st.sidebar.warning("⚠️ Only administrators can upload documents to the shared knowledge base.")
    
    # Display shared knowledge base stats for all users
    if st.session_state.documents:
        st.sidebar.subheader("📚 Shared Knowledge Base")
        st.sidebar.info(f"Total chunks: {len(st.session_state.documents)}")
        
        # Grounding settings for all users
        st.sidebar.subheader("🎯 Query Settings")
        st.session_state.grounding_threshold = st.sidebar.slider(
            "Response Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values require stronger grounding to source documents"
        )

        # Only admin can clear knowledge base
        if current_user and current_user.role == UserRole.ADMIN:
            if st.sidebar.button("🗑️ Clear Knowledge Base (Admin)"):
                st.session_state.documents = []
                from DIGITAL_COMPANION_APP import RAGVectorStore
                st.session_state.vector_store = RAGVectorStore(st.session_state.embeddings_model)
                st.sidebar.success("Knowledge base cleared!")
                st.rerun()

def render_user_info_sidebar(current_user: User):
    """Render user information in sidebar"""
    if current_user:
        st.sidebar.markdown(f"""
        <div class="metric-card">
            <strong>👤 User:</strong> {current_user.name}<br>
            <strong>🎭 Role:</strong> {current_user.role.value.title()}<br>
            <strong>📧 Session:</strong> Active
        </div>
        """, unsafe_allow_html=True)

def render_grounding_info(grounding_result: Dict[str, Any]):
    """Render grounding confidence information"""
    if not grounding_result:
        return
        
    # Color code based on grounding quality
    if grounding_result['confidence'] >= 0.8:
        confidence_color = "🟢"
    elif grounding_result['confidence'] >= 0.6:
        confidence_color = "🟡"
    else:
        confidence_color = "🔴"

    st.markdown(f"{confidence_color} **Grounding Confidence:** {grounding_result['confidence']:.2f}")

    with st.expander("🔍 Grounding Details"):
        st.write(f"**Well Grounded:** {'Yes' if grounding_result['is_grounded'] else 'No'}")
        st.write(f"**Text Overlap:** {grounding_result['text_overlap']:.2f}")
        st.write(f"**Semantic Similarity:** {grounding_result['semantic_similarity']:.2f}")
        st.write(f"**Reason:** {grounding_result['reason']}")

def render_sources_info(sources: List[Dict[str, Any]]):
    """Render source information"""
    if not sources:
        return
        
    with st.expander("📚 Sources"):
        for i, source in enumerate(sources):
            st.markdown(f"**Source {i + 1}** (Relevance: {source.get('relevance_score', 0):.2f})")
            metadata = source.get('metadata', {})
            st.markdown(f"*Type:* {metadata.get('source_type', 'Unknown')}")
            st.markdown(f"*File:* {metadata.get('source_file', 'Unknown')}")
            content = source.get('content', '')
            st.code(content[:300] + "..." if len(content) > 300 else content)