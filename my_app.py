import streamlit as st
import sqlite3

# Define a function to establish a connection to SQLite database
def get_db_connection():
    conn = sqlite3.connect('math_quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define User model
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password  # Store plain text password

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

    def check_password(self, password):
        # Compare the plain text password with the stored password
        return self.password == password

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
        print(f"Debug: Retrieved {len(questions)} questions for grade {grade}")  # Debug statement
        return questions

# Initialize the database and create tables if they don't exist
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_option TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Prepopulate the database with questions for each grade
def populate_questions():
    questions_by_grade = {
        1: [
            ("What is 2 + 2?", "3,4,5", "4"),
            ("What is 5 - 3?", "1,2,3", "2"),
            ("What is 3 + 1?", "3,4,5", "4"),
            ("What is 6 - 2?", "3,4,5", "4"),
            ("What is 1 + 2?", "2,3,4", "3"),
        ],
        2: [
            ("What is 7 + 3?", "9,10,11", "10"),
            ("What is 8 - 5?", "2,3,4", "3"),
            ("What is 4 + 5?", "8,9,10", "9"),
            ("What is 10 - 4?", "5,6,7", "6"),
            ("What is 2 + 6?", "7,8,9", "8"),
        ],
        3: [
            ("What is 5 * 2?", "8,9,10", "10"),
            ("What is 9 / 3?", "2,3,4", "3"),
            ("What is 6 + 4?", "9,10,11", "10"),
            ("What is 15 - 5?", "8,9,10", "10"),
            ("What is 3 * 3?", "6,8,9", "9"),
        ],
        4: [
            ("What is 12 / 4?", "2,3,4", "3"),
            ("What is 7 * 3?", "20,21,22", "21"),
            ("What is 16 - 7?", "8,9,10", "9"),
            ("What is 5 * 4?", "19,20,21", "20"),
            ("What is 25 / 5?", "4,5,6", "5"),
        ],
        5: [
            ("What is 14 + 7?", "20,21,22", "21"),
            ("What is 18 / 2?", "7,8,9", "9"),
            ("What is 11 * 2?", "21,22,23", "22"),
            ("What is 24 - 9?", "14,15,16", "15"),
            ("What is 30 / 3?", "9,10,11", "10"),
        ],
        6: [
            ("What is 15 * 2?", "28,29,30", "30"),
            ("What is 18 / 6?", "2,3,4", "3"),
            ("What is 25 + 12?", "36,37,38", "37"),
            ("What is 40 - 15?", "24,25,26", "25"),
            ("What is 21 / 3?", "6,7,8", "7"),
        ],
        7: [
            ("What is 32 / 8?", "3,4,5", "4"),
            ("What is 7 * 5?", "34,35,36", "35"),
            ("What is 45 - 18?", "26,27,28", "27"),
            ("What is 28 / 4?", "6,7,8", "7"),
            ("What is 13 * 3?", "38,39,40", "39"),
        ],
        8: [
            ("What is 64 / 8?", "7,8,9", "8"),
            ("What is 14 * 2?", "27,28,29", "28"),
            ("What is 75 - 35?", "38,39,40", "40"),
            ("What is 24 / 6?", "3,4,5", "4"),
            ("What is 17 * 2?", "33,34,35", "34"),
        ],
        9: [
            ("What is 81 / 9?", "8,9,10", "9"),
            ("What is 23 + 27?", "49,50,51", "50"),
            ("What is 15 * 4?", "59,60,61", "60"),
            ("What is 50 / 5?", "9,10,11", "10"),
            ("What is 19 * 3?", "56,57,58", "57"),
        ],
        10: [
            ("What is 100 / 10?", "9,10,11", "10"),
            ("What is 12 * 12?", "143,144,145", "144"),
            ("What is 77 - 33?", "43,44,45", "44"),
            ("What is 90 / 9?", "9,10,11", "10"),
            ("What is 21 * 5?", "104,105,106", "105"),
        ],
        11: [
            ("What is 144 / 12?", "10,11,12", "12"),
            ("What is 13 * 13?", "168,169,170", "169"),
            ("What is 110 - 45?", "64,65,66", "65"),
            ("What is 121 / 11?", "10,11,12", "11"),
            ("What is 24 * 6?", "143,144,145", "144"),
        ],
        12: [
            ("What is 169 / 13?", "12,13,14", "13"),
            ("What is 15 * 15?", "224,225,226", "225"),
            ("What is 200 - 75?", "124,125,126", "125"),
            ("What is 144 / 12?", "11,12,13", "12"),
            ("What is 20 * 8?", "159,160,161", "160"),
        ],
    }

    for grade, questions in questions_by_grade.items():
        for question_text, options, correct_option in questions:
            question = Question(grade, question_text, options, correct_option)
            question.save()

# Streamlit application
def main():
    st.set_page_config(page_title="Math Quiz App", page_icon="🧮", layout="wide")

    # Initialize session state
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'step' not in st.session_state:
        st.session_state.step = 'login_or_register'

    # Define navigation functions
    def navigate_to(step):
        st.session_state.step = step

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
                        if user and user['password'] == password_login:  # Check plain text password
                            st.success("Login successful")
                            st.session_state.username = username_login
                            navigate_to('grade_select')
                        else:
                            st.error("Invalid credentials")

if __name__ == "__main__":
    main()

# Streamlit application
def main():
    st.markdown("""
        <style>
        body {
            background-color: #2c3e50;
        }
        h1, h2, h3, h4, h5, h6, p, div, span {
            color: #ecf0f1;
        }
        .stButton button {
            background-color: #e74c3c;
            color: white;
        }
        .stButton button:hover {
            background-color: #c0392b;
            color: white;
        }
        .stTextInput>div>div>input {
            color: black;
        }
        .stTextArea>div>textarea {
            color: black;
        }
        .stRadio>div>div>label {
            color: white;
        }
        .stSelectbox>div>div>label {
            color: white;
        }
        .stSelectbox>div>div>div>div>div {
            color: black;
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

    # Initialize session state
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'step' not in st.session_state:
        st.session_state.step = 'login_or_register'
    if 'grade' not in st.session_state:
        st.session_state.grade = None
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'score' not in st.session_state:
        st.session_state.score = 0

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

        
    # Grade selection
    if st.session_state.step == 'grade_select':
        st.header("Select Grade")
        grade = st.selectbox("Grade", list(range(1, 13)), key="grade_select")
        st.session_state.grade = grade
        
        if st.button("Start Quiz", key="start_quiz_button"):
            questions = Question.get_by_grade(grade)
            if questions:
                st.session_state.questions = questions
                st.session_state.score = 0
                navigate_to('quiz')
            else:
                st.warning("No questions available for this grade.")
        
        if st.button("Back", key="grade_select_back_button"):
            go_back()
    
    # Quiz section
    if st.session_state.step == 'quiz' and st.session_state.username:
        questions = st.session_state.questions
        if questions:
            for question in questions:
                st.subheader(question['question_text'])
                options = question['options'].split(',')
                answer = st.radio("Options", options, key=f"question_{question['id']}")
                if answer == question['correct_option']:
                    st.session_state.score += 1
            st.success(f"Your score is {st.session_state.score}/{len(questions)}")
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
            st.sidebar.markdown("- *Name:* Ankit Dubey")
            st.sidebar.markdown("- *Contact No.:* 9619924069")

if __name__ == "__main__":
    # Initialize the database and populate questions if database is empty
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM questions")
    if c.fetchone()[0] == 0:
        populate_questions()
    conn.close()
    
    main()

