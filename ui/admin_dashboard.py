# ui/admin_dashboard.py
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from models.user import User, UserRole
from services.auth_service import AuthService
from services.activity_service import ActivityService
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def render_admin_dashboard(current_user: User, auth_service: AuthService, activity_service: ActivityService):
    """Render comprehensive admin dashboard for AERO system management"""
    st.header("🔧 AERO System Administration")
    
    # Admin dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 User Management", 
        "📊 System Analytics", 
        "📚 Knowledge Base", 
        "⚡ Performance", 
        "🔒 Security"
    ])
    
    with tab1:
        _render_user_management(auth_service)
    
    with tab2:
        _render_system_analytics(activity_service)
    
    with tab3:
        _render_knowledge_base_management()
    
    with tab4:
        _render_performance_monitoring()
    
    with tab5:
        _render_security_dashboard()

def _render_user_management(auth_service: AuthService):
    """Render user management interface"""
    st.subheader("👥 User Management")
    
    # User creation section
    with st.expander("➕ Create New User", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Username", placeholder="Enter username")
            new_name = st.text_input("Full Name", placeholder="Enter full name")
            new_email = st.text_input("Email", placeholder="Enter email address")
        
        with col2:
            new_role = st.selectbox("Role", ["student", "teacher", "parent", "admin"])
            new_password = st.text_input("Password", type="password", placeholder="Enter password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
        
        if st.button("🔄 Create User"):
            if new_password == confirm_password and new_username and new_name:
                try:
                    success = auth_service.create_user(
                        username=new_username,
                        password=new_password,
                        name=new_name,
                        email=new_email,
                        role=UserRole(new_role)
                    )
                    if success:
                        st.success(f"✅ User {new_username} created successfully!")
                    else:
                        st.error("❌ Failed to create user - username might already exist")
                except Exception as e:
                    st.error(f"❌ Error creating user: {e}")
            else:
                st.error("❌ Please fill all fields and ensure passwords match")
    
    # Existing users management
    st.subheader("📋 Existing Users")
    
    # Mock user data - replace with real database query
    users_data = _get_mock_users_data()
    
    if users_data:
        df_users = pd.DataFrame(users_data)
        
        # User statistics
        col1, col2, col3, col4 = st.columns(4)
        
        role_counts = df_users['role'].value_counts()
        with col1:
            st.metric("Total Users", len(df_users), "↗️ +12%")
        with col2:
            st.metric("Students", role_counts.get('student', 0), "↗️ +8%")
        with col3:
            st.metric("Teachers", role_counts.get('teacher', 0), "↗️ +2%")
        with col4:
            st.metric("Parents", role_counts.get('parent', 0), "↗️ +15%")
        
        # Users table with actions
        st.dataframe(
            df_users[['username', 'name', 'role', 'email', 'last_active', 'is_active']],
            column_config={
                'username': 'Username',
                'name': 'Full Name', 
                'role': st.column_config.SelectboxColumn('Role', options=['student', 'teacher', 'parent', 'admin']),
                'email': 'Email',
                'last_active': 'Last Active',
                'is_active': st.column_config.CheckboxColumn('Active')
            },
            use_container_width=True
        )
        
        # Bulk actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send Welcome Emails"):
                st.info("Feature coming soon - Email notifications")
        
        with col2:
            if st.button("🔒 Deactivate Inactive Users"):
                st.warning("This will deactivate users inactive for 30+ days")
        
        with col3:
            if st.button("📊 Export User List"):
                csv = df_users.to_csv(index=False)
                st.download_button("Download CSV", csv, "users_export.csv", "text/csv")

def _render_system_analytics(activity_service: ActivityService):
    """Render system-wide analytics"""
    st.subheader("📊 System Analytics")
    
    # Mock analytics data
    analytics_data = _get_mock_system_analytics()
    
    # System overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Daily Active Users", analytics_data['dau'], "↗️ +23%")
    with col2:
        st.metric("Total Queries Today", analytics_data['queries_today'], "↗️ +45%")
    with col3:
        st.metric("Avg Response Time", f"{analytics_data['avg_response_time']}ms", "↘️ -15%")
    with col4:
        st.metric("System Uptime", f"{analytics_data['uptime']}%", "🟢 Excellent")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily usage trend
        usage_data = pd.DataFrame(analytics_data['daily_usage'])
        fig = px.line(usage_data, x='date', y='users', 
                     title="Daily Active Users Trend",
                     markers=True)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Query distribution by role
        role_data = pd.DataFrame(analytics_data['queries_by_role'])
        fig = px.pie(role_data, values='queries', names='role',
                     title="Queries by User Role",
                     color_discrete_map={
                         'student': '#1E88E5',
                         'teacher': '#43A047', 
                         'parent': '#FB8C00',
                         'admin': '#D32F2F'
                     })
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # System performance over time
    st.subheader("⚡ Performance Metrics")
    perf_data = pd.DataFrame(analytics_data['performance_timeline'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=perf_data['time'], y=perf_data['response_time'],
                            mode='lines+markers', name='Response Time (ms)',
                            line=dict(color='#FF6B6B')))
    
    fig.add_trace(go.Scatter(x=perf_data['time'], y=perf_data['concurrent_users'],
                            mode='lines+markers', name='Concurrent Users',
                            yaxis='y2', line=dict(color='#4ECDC4')))
    
    fig.update_layout(
        title="System Performance Timeline",
        xaxis_title="Time",
        yaxis=dict(title="Response Time (ms)", side='left'),
        yaxis2=dict(title="Concurrent Users", side='right', overlaying='y'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_knowledge_base_management():
    """Render knowledge base management"""
    st.subheader("📚 Knowledge Base Management")
    
    # Mock knowledge base stats
    kb_stats = {
        'total_documents': 847,
        'total_chunks': 12543,
        'total_size_mb': 156.7,
        'document_types': [
            {'type': 'PDF', 'count': 342, 'size_mb': 89.2},
            {'type': 'Text', 'count': 298, 'size_mb': 23.4},
            {'type': 'Video', 'count': 156, 'size_mb': 34.8},
            {'type': 'YouTube', 'count': 51, 'size_mb': 9.3}
        ]
    }
    
    # Knowledge base overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", kb_stats['total_documents'], "↗️ +34")
    with col2:
        st.metric("Knowledge Chunks", f"{kb_stats['total_chunks']:,}", "↗️ +567")
    with col3:
        st.metric("Storage Used", f"{kb_stats['total_size_mb']:.1f} MB", "↗️ +12.3MB")
    with col4:
        st.metric("Coverage Score", "87%", "↗️ +5%")
    
    # Document type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        df_types = pd.DataFrame(kb_stats['document_types'])
        fig = px.bar(df_types, x='type', y='count',
                     title="Documents by Type",
                     color='type',
                     color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(df_types, values='size_mb', names='type',
                     title="Storage by Document Type",
                     color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Knowledge base actions
    st.subheader("🔧 Knowledge Base Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Rebuild Vector Index"):
            st.info("This will rebuild the entire FAISS vector index")
    
    with col2:
        if st.button("🗑️ Clean Orphaned Chunks"):
            st.info("This will remove chunks without source documents")
    
    with col3:
        if st.button("📊 Export Knowledge Map"):
            st.info("Generate knowledge base coverage report")

def _render_performance_monitoring():
    """Render performance monitoring dashboard"""
    st.subheader("⚡ Performance Monitoring")
    
    # Mock performance data
    perf_data = {
        'current_load': {
            'cpu_usage': 34.2,
            'memory_usage': 67.8,
            'disk_usage': 23.1,
            'network_io': 45.6
        },
        'response_times': {
            'p50': 680,
            'p95': 1200,
            'p99': 2100
        },
        'cache_stats': {
            'hit_rate': 73.4,
            'miss_rate': 26.6,
            'cache_size_mb': 234.7
        }
    }
    
    # Current system load
    st.subheader("🖥️ Current System Load")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CPU Usage", f"{perf_data['current_load']['cpu_usage']:.1f}%", 
                 "🟢 Normal" if perf_data['current_load']['cpu_usage'] < 80 else "🔴 High")
    with col2:
        st.metric("Memory Usage", f"{perf_data['current_load']['memory_usage']:.1f}%",
                 "🟡 Moderate" if perf_data['current_load']['memory_usage'] < 80 else "🔴 High")
    with col3:
        st.metric("Disk Usage", f"{perf_data['current_load']['disk_usage']:.1f}%", "🟢 Low")
    with col4:
        st.metric("Network I/O", f"{perf_data['current_load']['network_io']:.1f}%", "🟢 Normal")
    
    # Response time percentiles
    st.subheader("⏱️ Response Time Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        percentiles = ['p50', 'p95', 'p99']
        times = [perf_data['response_times'][p] for p in percentiles]
        
        fig = px.bar(x=percentiles, y=times, 
                     title="Response Time Percentiles",
                     labels={'x': 'Percentile', 'y': 'Response Time (ms)'},
                     color=times, color_continuous_scale='RdYlGn_r')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cache performance
        cache_data = [
            {'status': 'Hit', 'percentage': perf_data['cache_stats']['hit_rate']},
            {'status': 'Miss', 'percentage': perf_data['cache_stats']['miss_rate']}
        ]
        df_cache = pd.DataFrame(cache_data)
        
        fig = px.pie(df_cache, values='percentage', names='status',
                     title="Cache Hit/Miss Ratio",
                     color_discrete_map={'Hit': '#4ECDC4', 'Miss': '#FF6B6B'})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cache information
    st.info(f"📋 Cache Size: {perf_data['cache_stats']['cache_size_mb']:.1f} MB | Hit Rate: {perf_data['cache_stats']['hit_rate']:.1f}%")

def _render_security_dashboard():
    """Render security monitoring dashboard"""
    st.subheader("🔒 Security Dashboard")
    
    # Mock security data
    security_data = {
        'failed_logins': 23,
        'active_sessions': 89,
        'suspicious_queries': 7,
        'blocked_ips': 12,
        'recent_security_events': [
            {'time': '2025-09-05 10:30', 'event': 'Failed login attempt', 'user': 'unknown', 'ip': '192.168.1.100'},
            {'time': '2025-09-05 09:15', 'event': 'Suspicious query pattern', 'user': 'student23', 'ip': '10.0.0.50'},
            {'time': '2025-09-05 08:45', 'event': 'Multiple rapid queries', 'user': 'bot_user', 'ip': '203.45.67.89'},
        ]
    }
    
    # Security metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Failed Logins (24h)", security_data['failed_logins'], 
                 "🔴 +5" if security_data['failed_logins'] > 20 else "🟢 Normal")
    with col2:
        st.metric("Active Sessions", security_data['active_sessions'], "🟢 Normal")
    with col3:
        st.metric("Suspicious Queries", security_data['suspicious_queries'], 
                 "🟡 Monitor" if security_data['suspicious_queries'] > 5 else "🟢 Low")
    with col4:
        st.metric("Blocked IPs", security_data['blocked_ips'], "🟢 Effective")
    
    # Recent security events
    st.subheader("🚨 Recent Security Events")
    df_events = pd.DataFrame(security_data['recent_security_events'])
    
    if not df_events.empty:
        st.dataframe(
            df_events,
            column_config={
                'time': 'Timestamp',
                'event': 'Event Type',
                'user': 'User',
                'ip': 'IP Address'
            },
            use_container_width=True
        )
    
    # Security actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔒 Force Password Reset"):
            st.warning("This will require all users to reset passwords")
    
    with col2:
        if st.button("🚫 Block Suspicious IPs"):
            st.info("Auto-block IPs with multiple failed attempts")
    
    with col3:
        if st.button("📋 Export Security Log"):
            st.info("Generate comprehensive security report")

def _get_mock_users_data():
    """Generate mock user data for demonstration"""
    return [
        {
            'username': 'admin1',
            'name': 'System Administrator',
            'role': 'admin',
            'email': 'admin@school.edu',
            'last_active': '2025-09-05 11:30',
            'is_active': True
        },
        {
            'username': 'teacher1',
            'name': 'Ms. Sarah Johnson',
            'role': 'teacher',
            'email': 'sarah.johnson@school.edu',
            'last_active': '2025-09-05 10:45',
            'is_active': True
        },
        {
            'username': 'student123',
            'name': 'Alex Chen',
            'role': 'student',
            'email': 'alex.chen@student.school.edu',
            'last_active': '2025-09-05 11:25',
            'is_active': True
        },
        {
            'username': 'parent_chen',
            'name': 'David Chen',
            'role': 'parent',
            'email': 'david.chen@parent.school.edu',
            'last_active': '2025-09-05 09:30',
            'is_active': True
        },
        {
            'username': 'student456',
            'name': 'Emma Rodriguez',
            'role': 'student',
            'email': 'emma.rodriguez@student.school.edu',
            'last_active': '2025-09-04 16:20',
            'is_active': True
        }
    ]

def _get_mock_system_analytics():
    """Generate mock system analytics data"""
    return {
        'dau': 342,
        'queries_today': 1247,
        'avg_response_time': 750,
        'uptime': 99.7,
        'daily_usage': [
            {'date': '2025-08-30', 'users': 298},
            {'date': '2025-08-31', 'users': 312},
            {'date': '2025-09-01', 'users': 285},
            {'date': '2025-09-02', 'users': 356},
            {'date': '2025-09-03', 'users': 334},
            {'date': '2025-09-04', 'users': 342},
        ],
        'queries_by_role': [
            {'role': 'student', 'queries': 875},
            {'role': 'teacher', 'queries': 234},
            {'role': 'parent', 'queries': 98},
            {'role': 'admin', 'queries': 40}
        ],
        'performance_timeline': [
            {'time': '08:00', 'response_time': 650, 'concurrent_users': 45},
            {'time': '10:00', 'response_time': 720, 'concurrent_users': 89},
            {'time': '12:00', 'response_time': 890, 'concurrent_users': 134},
            {'time': '14:00', 'response_time': 756, 'concurrent_users': 112},
            {'time': '16:00', 'response_time': 823, 'concurrent_users': 95},
            {'time': '18:00', 'response_time': 678, 'concurrent_users': 67}
        ]
    }