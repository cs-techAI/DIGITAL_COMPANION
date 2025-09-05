# ui/teacher_dashboard.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any
from models.user import User
from services.activity_service import ActivityService
from datetime import datetime, timedelta
import collections

def render_teacher_dashboard(current_user: User, activity_service: ActivityService):
    """Render teacher analytics dashboard"""
    st.header("📊 AERO Teacher Analytics")
    
    # Get all student activities for analytics
    try:
        # Mock data for now - replace with actual database queries
        activities_data = _get_mock_analytics_data()
        
        if not activities_data:
            st.info("📚 No student activity data available yet. Students need to start asking questions!")
            return
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", activities_data['total_students'], "↗️ +12%")
        with col2:
            st.metric("Questions Today", activities_data['questions_today'], "↗️ +45%")
        with col3:
            st.metric("Avg Response Time", f"{activities_data['avg_response_time']}ms", "↘️ -15%")
        with col4:
            st.metric("Knowledge Coverage", f"{activities_data['coverage_percent']}%", "↗️ +8%")
        
        # Tabs for different analytics
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Popular Topics", "👥 Student Activity", "📈 Trends"])
        
        with tab1:
            _render_overview_charts(activities_data)
        
        with tab2:
            _render_topic_analysis(activities_data)
        
        with tab3:
            _render_student_activity(activities_data)
        
        with tab4:
            _render_trend_analysis(activities_data)
            
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def _get_mock_analytics_data():
    """Generate mock analytics data - replace with real database queries"""
    return {
        'total_students': 127,
        'questions_today': 89,
        'avg_response_time': 850,
        'coverage_percent': 73,
        'popular_topics': [
            {'topic': 'Photosynthesis', 'count': 45, 'avg_difficulty': 'Medium'},
            {'topic': 'Cell Division', 'count': 38, 'avg_difficulty': 'Hard'},
            {'topic': 'DNA Structure', 'count': 32, 'avg_difficulty': 'Medium'},
            {'topic': 'Protein Synthesis', 'count': 28, 'avg_difficulty': 'Hard'},
            {'topic': 'Respiration', 'count': 25, 'avg_difficulty': 'Easy'},
        ],
        'daily_questions': [
            {'date': '2025-08-30', 'questions': 45},
            {'date': '2025-08-31', 'questions': 52},
            {'date': '2025-09-01', 'questions': 38},
            {'date': '2025-09-02', 'questions': 67},
            {'date': '2025-09-03', 'questions': 71},
            {'date': '2025-09-04', 'questions': 89},
        ],
        'student_engagement': [
            {'student': 'Alice J.', 'questions': 23, 'topics': 8, 'avg_score': 87},
            {'student': 'Bob M.', 'questions': 19, 'topics': 6, 'avg_score': 92},
            {'student': 'Carol S.', 'questions': 31, 'topics': 12, 'avg_score': 78},
            {'student': 'David L.', 'questions': 15, 'topics': 5, 'avg_score': 95},
            {'student': 'Emma R.', 'questions': 27, 'topics': 9, 'avg_score': 83},
        ],
        'difficulty_distribution': [
            {'difficulty': 'Easy', 'count': 89, 'avg_time': 650},
            {'difficulty': 'Medium', 'count': 134, 'avg_time': 850},
            {'difficulty': 'Hard', 'count': 67, 'avg_time': 1200},
        ]
    }

def _render_overview_charts(data):
    """Render overview analytics charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Question Volume")
        df_daily = pd.DataFrame(data['daily_questions'])
        fig = px.line(df_daily, x='date', y='questions', 
                     title="Questions Asked Per Day",
                     markers=True)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Difficulty Distribution")
        df_diff = pd.DataFrame(data['difficulty_distribution'])
        fig = px.pie(df_diff, values='count', names='difficulty',
                     title="Question Difficulty Levels",
                     color_discrete_map={'Easy': '#90EE90', 'Medium': '#FFD700', 'Hard': '#FF6B6B'})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

def _render_topic_analysis(data):
    """Render topic analysis"""
    st.subheader("🔍 Most Popular Topics")
    
    # Popular topics table
    df_topics = pd.DataFrame(data['popular_topics'])
    
    # Create horizontal bar chart
    fig = px.bar(df_topics, x='count', y='topic', orientation='h',
                 title="Questions by Topic", 
                 color='avg_difficulty',
                 color_discrete_map={'Easy': '#90EE90', 'Medium': '#FFD700', 'Hard': '#FF6B6B'})
    fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Topic insights
    st.subheader("💡 Topic Insights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Most Popular:** {data['popular_topics'][0]['topic']}\n{data['popular_topics'][0]['count']} questions")
    with col2:
        hard_topics = [t for t in data['popular_topics'] if t['avg_difficulty'] == 'Hard']
        if hard_topics:
            st.warning(f"**Most Challenging:** {hard_topics[0]['topic']}\nStudents need extra help")
    with col3:
        total_questions = sum(t['count'] for t in data['popular_topics'])
        st.success(f"**Total Coverage:** {len(data['popular_topics'])} topics\n{total_questions} total questions")

def _render_student_activity(data):
    """Render student activity analysis"""
    st.subheader("👥 Student Engagement")
    
    df_students = pd.DataFrame(data['student_engagement'])
    
    # Student engagement scatter plot
    fig = px.scatter(df_students, x='questions', y='avg_score', size='topics',
                     hover_name='student', title="Student Engagement vs Performance",
                     labels={'questions': 'Questions Asked', 'avg_score': 'Average Score'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top students table
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏆 Top Performers")
        df_sorted = df_students.sort_values('avg_score', ascending=False)
        st.dataframe(
            df_sorted[['student', 'questions', 'topics', 'avg_score']],
            column_config={
                'student': 'Student',
                'questions': st.column_config.NumberColumn('Questions', format='%d'),
                'topics': st.column_config.NumberColumn('Topics', format='%d'),
                'avg_score': st.column_config.ProgressColumn('Avg Score', min_value=0, max_value=100)
            },
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.subheader("📊 Quick Stats")
        avg_questions = df_students['questions'].mean()
        avg_topics = df_students['topics'].mean()
        avg_performance = df_students['avg_score'].mean()
        
        st.metric("Avg Questions/Student", f"{avg_questions:.1f}")
        st.metric("Avg Topics/Student", f"{avg_topics:.1f}")
        st.metric("Class Average", f"{avg_performance:.1f}%")

def _render_trend_analysis(data):
    """Render trend analysis"""
    st.subheader("📈 Learning Trends")
    
    # Response time analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏱️ Response Time by Difficulty")
        df_diff = pd.DataFrame(data['difficulty_distribution'])
        fig = px.bar(df_diff, x='difficulty', y='avg_time',
                     title="Average Response Time by Difficulty",
                     color='avg_time', color_continuous_scale='RdYlGn_r')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Recommendations")
        st.info("""
        **Key Insights:**
        • Students struggle most with Cell Division
        • Response times increase with difficulty  
        • High engagement with Photosynthesis topic
        
        **Recommendations:**
        • Add more Cell Division examples
        • Create interactive tutorials for hard topics
        • Encourage peer discussion groups
        """)
    
    # Weekly trends
    st.subheader(" Weekly Learning Pattern")
    df_daily = pd.DataFrame(data['daily_questions'])
    df_daily['day_of_week'] = pd.to_datetime(df_daily['date']).dt.day_name()
    
    # Group by day of week
    weekly_pattern = df_daily.groupby('day_of_week')['questions'].mean().reset_index()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_pattern['day_of_week'] = pd.Categorical(weekly_pattern['day_of_week'], categories=day_order, ordered=True)
    weekly_pattern = weekly_pattern.sort_values('day_of_week')
    
    fig = px.bar(weekly_pattern, x='day_of_week', y='questions',
                 title="Average Questions by Day of Week")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)