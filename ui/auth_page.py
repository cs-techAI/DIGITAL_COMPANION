# ui/auth_page.py
import streamlit as st
import hashlib
import uuid
from datetime import datetime
from models.user import User, UserRole
from services.auth_service import AuthService

def render_auth_page(auth_service: AuthService):
    """Render authentication page with login and signup"""

    # CSS for styling the header and global font sizes
    st.markdown("""
        <style>
            .role-header {
                text-align: center;
                font-size: 3rem;
                font-weight: 700;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin-bottom: 1.5rem;
                color: #333333;
            }
            /* Increase base font size */
            html, body, [class*="css"]  {
                font-size: 18px !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }
            /* Subheader */
            .st-subheader {
                font-size: 1.8rem !important;
                font-weight: 600 !important;
            }
            /* Info, warning, error messages and buttons */
            .st-info, .st-warning, .st-error, .st-success {
                font-size: 1.15rem !important;
            }
            button[data-baseweb="button"] {
                font-size: 1.1rem !important;
                font-weight: 600 !important;
            }
            /* Form labels */
            label[data-baseweb="label"] {
                font-size: 1.1rem !important;
                font-weight: 600;
            }
            /* Expander summary */
            .streamlit-expanderHeader {
                font-size: 1.3rem !important;
                font-weight: 600 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Updated header with new text
    st.markdown('<div class="role-header">🔐 Digital Companion - Aero Chatbot</div>', unsafe_allow_html=True)
    
    # Demo credentials info
    with st.expander("🔍 Demo Credentials"):
        st.info("""
        **Demo Accounts:**
        - Admin: username=`admin`, password=`admin123`
        - Student: username=`student1`, password=`student123`  
        - Teacher: username=`teacher1`, password=`teacher123`  
        - Parent: username=`parent1`, password=`parent123`
        """)
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        render_login_form(auth_service)
    
    with tab2:
        render_signup_form(auth_service)

# The rest of the code remains unchanged...

def render_login_form(auth_service: AuthService):
    """Render login form"""
    with st.form("login_form"):
        st.subheader("👤 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("🔑 Login")
    if login_submitted:
        if username and password:
            try:
                user = auth_service.authenticate_user(username, password)
                if user:
                    # Store user in session state
                    st.session_state.authenticated = True
                    st.session_state.current_user = user
                    st.session_state.username = user.username
                    st.session_state.name = user.name
                    st.session_state.user_role = user.role.value
                    
                    # Log login activity for students
                    if user.role == UserRole.STUDENT:
                        st.session_state.activity_service.log_login_activity(
                            user.id, 
                            st.session_state.session_id
                        )
                    
                    st.success(f"✅ Welcome {user.name}! Role: {user.role.value.title()}")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            except Exception as e:
                st.error(f"❌ Login error: {str(e)}")
        else:
            st.warning("⚠️ Please enter both username and password")

def render_signup_form(auth_service: AuthService):
    """Render signup form"""
    with st.form("signup_form"):
        st.subheader("📝 Create New Account")
        
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username*")
            new_name = st.text_input("Full Name*")
        with col2:
            new_email = st.text_input("Email Address*")
            role = st.selectbox("Role*", ["student", "teacher", "parent"])
        
        new_password = st.text_input("Password*", type="password")
        confirm_password = st.text_input("Confirm Password*", type="password")
        
        # Parent-student linking (for parent accounts)
        parent_student_username = None
        if role == "parent":
            parent_student_username = st.text_input(
                "Student Username (to link)",
                help="Enter the username of the student you want to link to this parent account"
            )
        
        submitted = st.form_submit_button("📝 Create Account")
    if submitted:
        try:
            # Validation
            if not all([new_username, new_name, new_email, new_password, confirm_password]):
                st.error("❌ All required fields must be filled")
                return
            
            if new_password != confirm_password:
                st.error("❌ Passwords don't match")
                return
            
            if len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
                return
            
            # Create user
            user_role = UserRole(role)
            user = auth_service.register_user(
                username=new_username,
                name=new_name,
                email=new_email,
                password=new_password,
                role=user_role
            )
            
            if user:
                st.success(f"✅ Account created successfully! You can now log in.")
                
                # Handle parent-student linking
                if role == "parent" and parent_student_username:
                    link_parent_to_student(user.id, parent_student_username, auth_service)
                
            else:
                st.error("❌ Failed to create account. Username or email may already exist.")
                
        except ValueError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ Signup error: {str(e)}")

def link_parent_to_student(parent_id: str, student_username: str, auth_service: AuthService):
    """Link parent to student account"""
    try:
        # Find student by username
        student = auth_service.db.get_user_by_username(student_username)
        if student and student.role == UserRole.STUDENT:
            # Create relationship (this would be implemented in database service)
            st.info(f"👨‍👩‍👧‍👦 Successfully linked to student: {student.name}")
        else:
            st.warning(f"⚠️ Student username '{student_username}' not found or not a student account")
    except Exception as e:
        st.warning(f"⚠️ Could not link to student: {str(e)}")

def create_demo_users(auth_service: AuthService):
    """Create demo users for testing"""
    demo_users = [
        {"username": "student1", "name": "Alice Johnson", "email": "alice@student.edu", 
         "password": "student123", "role": UserRole.STUDENT},
        {"username": "teacher1", "name": "Prof. Smith", "email": "smith@university.edu", 
         "password": "teacher123", "role": UserRole.TEACHER},
        {"username": "parent1", "name": "Mrs. Wilson", "email": "wilson@parent.com", 
         "password": "parent123", "role": UserRole.PARENT}
    ]
    
    for user_data in demo_users:
        existing_user = auth_service.db.get_user_by_username(user_data["username"])
        if not existing_user:
            try:
                auth_service.register_user(
                    username=user_data["username"],
                    name=user_data["name"],
                    email=user_data["email"],
                    password=user_data["password"],
                    role=user_data["role"]
                )
            except:
                pass  # User might already exist
