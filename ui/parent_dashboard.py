# ui/parent_dashboard.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any
from models.user import User
from services.activity_service import ActivityService
from datetime import datetime, timedelta

def render_parent_dashboard(current_user: User, activity_service: ActivityService):
    """Render parent dashboard with student progress"""
    st.header("👨‍👩‍👧‍👦 Parent Dashboard - Student Progress Monitor")
    
    # Get students linked to this parent
    students_summary = activity_service.get_students_for_parent_summary(current_user.id)
    
    if not students_summary:
        st.warning("📝 No students are linked to your account. Please contact an administrator to link student accounts.")
        st.info("""
        **To link students to your account:**
        1. Contact the system administrator
        2. Provide your username and your child's username
        3. Administrator will create the parent-student relationship
        """)
        return
    
    # Overview metrics
    st.subheader("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    total_queries = sum(s['progress'].total_queries if s['progress'] else 0 for s in students_summary)
    active_students = sum(1 for s in students_summary if s['progress'] and s['progress'].total_queries > 0)
    
    with col1:
        st.metric("👨‍👩‍👧‍👦 Students", len(students_summary))
    with col2:
        st.metric("💬 Total Queries (7 days)", total_queries)
    with col3:
        st.metric("🎯 Active Students", active_students)
    with col4:
        avg_satisfaction = sum(s['progress'].average_response_satisfaction if s['progress'] else 0 
                             for s in students_summary) / len(students_summary)
        st.metric("😊 Avg Satisfaction", f"{avg_satisfaction:.1f}/5")
    
    # Individual student progress
    st.subheader("📈 Individual Student Progress")
    
    for student_data in students_summary:
        student = student_data['student']
        progress = student_data['progress']
        
        with st.expander(f"📚 {student.name} (@{student.username})", expanded=True):
            if not progress:
                st.info("No recent activity in the last 7 days.")
                continue
            
            # Student metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Questions Asked", progress.total_queries)
            with col2:
                st.metric("Topics Explored", progress.unique_topics_explored)
            with col3:
                st.metric("Sessions/Week", f"{progress.sessions_per_week:.1f}")
            
            # Learning patterns
            st.write("**🕐 Most Active Hours:**")
            if progress.most_active_hours:
                hours_text = [f"{hour}:00" for hour in progress.most_active_hours]
                st.write(", ".join(hours_text))
            else:
                st.write("No data available")
            
            st.write("**📖 Preferred Topics:**")
            if progress.preferred_topics:
                topic_cols = st.columns(len(progress.preferred_topics))
                for i, topic in enumerate(progress.preferred_topics[:5]):
                    with topic_cols[i]:
                        st.write(f"• {topic.title()}")
            else:
                st.write("No topics identified yet")
            
            st.write("**🎓 Difficulty Progression:**")
            if progress.difficulty_progression:
                difficulty_text = " → ".join([d.title() for d in progress.difficulty_progression])
                st.write(difficulty_text)
            else:
                st.write("No difficulty data available")
    
    # Learning trends chart
    if total_queries > 0:
        st.subheader("📊 Learning Activity Trends")
        
        # Create sample data for visualization (in real implementation, get from database)
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
        
        chart_data = []
        for student_data in students_summary:
            student = student_data['student']
            progress = student_data['progress']
            if progress and progress.total_queries > 0:
                # Sample daily queries (in real implementation, get actual daily data)
                daily_queries = [max(0, progress.total_queries // 7 + (i % 3)) for i in range(7)]
                for date, queries in zip(dates, daily_queries):
                    chart_data.append({
                        'Date': date,
                        'Student': student.name,
                        'Queries': queries
                    })
        
        if chart_data:
            df = pd.DataFrame(chart_data)
            fig = px.line(df, x='Date', y='Queries', color='Student',
                         title="Daily Learning Activity",
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    # Topics distribution
    if students_summary:
        st.subheader("🎯 Topics Distribution")
        all_topics = []
        for student_data in students_summary:
            progress = student_data['progress']
            if progress and progress.preferred_topics:
                all_topics.extend(progress.preferred_topics)
        
        if all_topics:
            topic_counts = {}
            for topic in all_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            fig = px.pie(values=list(topic_counts.values()), 
                        names=list(topic_counts.keys()),
                        title="Learning Topics Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("💡 Learning Recommendations")
    for student_data in students_summary:
        student = student_data['student']
        progress = student_data['progress']
        
        if progress:
            st.write(f"**For {student.name}:**")
            
            recommendations = []
            
            # Activity-based recommendations
            if progress.sessions_per_week < 2:
                recommendations.append("📅 Encourage more regular study sessions (current: {:.1f}/week)".format(progress.sessions_per_week))
            
            if progress.unique_topics_explored < 3:
                recommendations.append("🌍 Explore more diverse topics to broaden knowledge")
            
            if progress.average_response_satisfaction < 3.5:
                recommendations.append("🤔 Consider asking more specific questions for better responses")
            
            if 'basic' in progress.difficulty_progression and len(progress.difficulty_progression) == 1:
                recommendations.append("⬆️ Try asking more detailed questions to advance learning")
            
            if not recommendations:
                recommendations.append("✅ Great job! Keep up the excellent learning pace!")
            
            for rec in recommendations:
                st.write(f"  • {rec}")
        
        st.write("---")
    
    # Export functionality
    st.subheader("📤 Export Progress Report")
    if st.button("📋 Generate Weekly Report"):
        generate_weekly_report(students_summary)

def generate_weekly_report(students_summary: List[Dict]):
    """Generate downloadable weekly progress report"""
    report_data = {
        'student_name': [],
        'total_queries': [],
        'topics_explored': [],
        'sessions_per_week': [],
        'satisfaction': [],
        'preferred_topics': []
    }
    
    for student_data in students_summary:
        student = student_data['student']
        progress = student_data['progress']
        
        if progress:
            report_data['student_name'].append(student.name)
            report_data['total_queries'].append(progress.total_queries)
            report_data['topics_explored'].append(progress.unique_topics_explored)
            report_data['sessions_per_week'].append(progress.sessions_per_week)
            report_data['satisfaction'].append(progress.average_response_satisfaction)
            report_data['preferred_topics'].append(', '.join(progress.preferred_topics))
        else:
            report_data['student_name'].append(student.name)
            for key in ['total_queries', 'topics_explored', 'sessions_per_week', 'satisfaction']:
                report_data[key].append(0)
            report_data['preferred_topics'].append('No activity')
    
    df = pd.DataFrame(report_data)
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name=f"student_progress_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )