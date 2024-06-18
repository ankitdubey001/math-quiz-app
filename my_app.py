import streamlit as st
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Define a function to establish a connection to SQLite database
def get_db_connection():
    conn = sqlite3.connect('math_quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define User model
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)
    
    def save(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (self.username, self.password))
        conn.commit()
        conn.close()
    
    @staticmethod
    def find_by_username(username):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        return user

# Define Question model
class Question:
    def __init__(self, grade, question_text, options, correct_option):
        self.grade = grade
        self.question_text = question_text
        self.options = options
        self.correct_option = correct_option
    
    def save(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO questions (grade, question_text, options, correct_option) VALUES (?, ?, ?, ?)', 
                  (self.grade, self.question_text, self.options, self.correct_option))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_by_grade(grade):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM questions WHERE grade = ?', (grade,))
        questions = c.fetchall()
        conn.close()
        return questions

# Prepopulate the database with questions for each grade
def populate_questions():
    questions_by_grade = {
        1: [
            ("What is 2 + 2?", "3,4,5", "4"),
            ("What is 5 - 3?", "1,2,3", "2"),
            # ... add more questions here
        ],
        2: [
            ("What is 7 + 3?", "9,10,11", "10"),
            ("What is 8 - 5?", "2,3,4", "3"),
            # ... add more questions here
        ],
        # Add questions for grades 3 to 12 similarly...
    }

    for grade, questions in questions_by_grade.items():
        for question_text, options, correct_option in questions:
            question = Question(grade, question_text, options, correct_option)
            question.save()

# Streamlit app
def main():
    st.set_page_config(page_title="Math Quiz App", page_icon="🧮", layout="wide")

    # CSS for customization
    st.markdown("""
        <style>
        .main {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        .stButton>button {
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
        }
        .stHeader {
            color: #ecf0f1;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        .stText {
            color: #ecf0f1;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        .container {
            padding: 20px;
            border: 2px solid #e74c3c;
            border-radius: 10px;
            background-color: #34495e;
            box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.3);
        }
        .stRadio>div {
            color: #ecf0f1;
        }
        .stSelectbox>div {
            color: #ecf0f1;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🧮 Math Quiz App", anchor=None)

    # Initialize session state
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'step' not in st.session_state:
        st.session_state.step = 'login_or_register'
    if 'grade' not in st.session_state:
        st.session_state.grade = None

    # Define navigation functions
    def navigate_to(step):
        st.session_state.step = step

    def go_back():
        if st.session_state.step == 'register':
            st.session_state.step = 'login_or_register'
        elif st.session_state.step == 'login':
            st.session_state.step = 'login_or_register'
        elif st.session_state.step == 'quiz':
            st.session_state.step = 'grade_select'
        elif st.session_state.step == 'grade_select':
            st.session_state.step = 'login_or_register'

    # Registration and Login
    if st.session_state.step == 'login_or_register':
        login_or_register = st.radio("Choose Action", ["Login", "Register"], key="action_select")
        
        if login_or_register == "Register":
            st.header("Register")
            with st.container():
                username_reg = st.text_input("Username", key="username_reg")
                password_reg = st.text_input("Password", type="password", key="password_reg")
                if st.button("Register", key="register_button"):
                    if not username_reg or not password_reg:
                        st.error("Please enter both username and password.")
                    elif User.find_by_username(username_reg):
                        st.error("Username already exists")
                    else:
                        new_user = User(username_reg, password_reg)
                        new_user.save()
                        st.success("Registration successful. Please log in.")
                        navigate_to('login')
                if st.button("Back", key="register_back_button"):
                    go_back()
        
        if login_or_register == "Login":
            st.header("Login")
            with st.container():
                username_login = st.text_input("Username", key="username_login")
                password_login = st.text_input("Password", type="password", key="password_login")
                if st.button("Login", key="login_button"):
                    if not username_login or not password_login:
                        st.error("Please enter both username and password.")
                    else:
                        user = User.find_by_username(username_login)
                        if user and check_password_hash(user['password'], password_login):
                            st.success("Login successful")
                            st.session_state.username = username_login
                            navigate_to('grade_select')
                        else:
                            st.error("Invalid credentials")
                if st.button("Back", key="login_back_button"):
                    go_back()
    
    # Grade selection
    if st.session_state.step == 'grade_select':
        st.header("Select Grade")
        grade = st.selectbox("Grade", list(range(1, 13)), key="grade_select")
        st.session_state.grade = grade
        
        if st.button("Start Quiz", key="start_quiz_button"):
            navigate_to('quiz')
        if st.button("Back", key="grade_select_back_button"):
            go_back()
    
    # Quiz section
    if st.session_state.step == 'quiz' and st.session_state.username:
        questions = Question.get_by_grade(st.session_state.grade)
        if questions:
            score = 0
            for question in questions:
                st.subheader(question['question_text'])
                options = question['options'].split(',')
                answer = st.radio("Options", options, key=f"question_{question['id']}")
                if answer == question['correct_option']:
                    score += 1
            st.success(f"Your score is {score}/{len(questions)}")
        else:
            st.warning("No questions available for this grade.")
        if st.button("Back", key="quiz_back_button"):
            go_back()
    
    # Add questions (for admin use, extend as needed)
    if st.session_state.username == 'admin' and st.session_state.step == 'grade_select':
        st.header("Add Question")
        with st.container():
            grade_add = st.selectbox("Grade for new question", list(range(1, 13)), key='grade_add')
            question_text_add = st.text_input("Question", key='question_text_add')
            options_add = st.text_area("Options (comma separated)", key='options_add').split(',')
            correct_option_add = st.text_input("Correct Option", key='correct_option_add')
            if st.button("Add Question", key="add_question_button"):
                if not question_text_add or not options_add or not correct_option_add:
                    st.error("Please enter all the fields.")
                else:
                    new_question = Question(grade_add, question_text_add, ','.join(options_add), correct_option_add)
                    new_question.save()
                    st.success("Question added successfully")
            if st.button("Back", key="admin_back_button"):
                go_back()
    
    # Display contact information button in sidebar
    if st.session_state.username:
        st.sidebar.markdown(
            """
            ### Contact Information
            Click the button below to view contact details.
            """
        )
        if st.sidebar.button("Contact Details", key="contact_button"):
            st.sidebar.markdown("- **Name:** Ankit Dubey")
            st.sidebar.markdown("- **Contact No.:** 9999955555")

if __name__ == "__main__":
    # Populate questions if database is empty
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM questions")
    if c.fetchone()[0] == 0:
        populate_questions()
    conn.close()
    
    main()
