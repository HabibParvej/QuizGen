import streamlit as st
from utils.extract_text import extract_text
from utils.quiz_generator import generate_quiz
from dotenv import load_dotenv
import os
import pandas as pd
import re
import json
import sqlite3
import hashlib
import time

# Correctly import missing LangChain and Groq modules
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('quizgen.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER,
        total_questions INTEGER,
        quiz_date TEXT,
        FOREIGN KEY (username) REFERENCES users (username)
    )''')
    conn.commit()
    conn.close()

init_db()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register user
def register_user(username, password):
    conn = sqlite3.connect('quizgen.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Authenticate user
def authenticate_user(username, password):
    conn = sqlite3.connect('quizgen.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

# Save score
def save_score(username, score, total_questions):
    conn = sqlite3.connect('quizgen.db')
    c = conn.cursor()
    c.execute("INSERT INTO scores (username, score, total_questions, quiz_date) VALUES (?, ?, ?, datetime('now'))",
             (username, score, total_questions))
    conn.commit()
    conn.close()

# Get leaderboard data
def get_leaderboard():
    conn = sqlite3.connect('quizgen.db')
    c = conn.cursor()
    c.execute("""
        SELECT 
            username, 
            MAX(score * 100.0 / total_questions) as percentage, 
            MAX(score) as score,
            MAX(total_questions) as total_questions,
            MAX(quiz_date) as quiz_date,
            COUNT(*) as attempts
        FROM scores
        GROUP BY username
        ORDER BY percentage DESC
        LIMIT 10
    """)
    results = c.fetchall()
    conn.close()
    return results

# Page configuration
st.set_page_config(
    page_title="📚 QuizGen",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional design with epic leaderboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

    /* Global styles */
    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
        color: #ffffff;
    }

    /* Header */
    .header {
        background: rgba(20, 20, 20, 0.95);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 204, 255, 0.1);
        transition: transform 0.3s ease;
    }
    .header:hover {
        transform: translateY(-5px);
    }
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00ccff;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        color: #a0a0a0;
    }

    /* Cards */
    .card {
        background: rgba(25, 25, 25, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 204, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #00ccff;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid rgba(0, 204, 255, 0.3);
        padding-bottom: 0.5rem;
    }

    /* Feature boxes */
    .feature-box {
        background: rgba(30, 30, 30, 0.9);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        transition: transform 0.3s ease, background 0.3s ease;
    }
    .feature-box:hover {
        transform: scale(1.05);
        background: rgba(0, 204, 255, 0.1);
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: #00ccff;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: #a0a0a0;
    }

    /* Quiz container */
    .quiz-container {
        background: rgba(25, 25, 25, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 204, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .quiz-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(0, 204, 255, 0.2);
    }
    .question-counter {
        background: rgba(0, 204, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        color: #ffffff;
    }
    .score-display {
        font-size: 1.2rem;
        font-weight: 600;
        color: #00ccff;
    }
    .question-text {
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
        color: #ffffff;
    }

    /* Feedback */
    .feedback-correct {
        color: #00ff99;
        padding: 1rem;
        background: rgba(0, 255, 153, 0.1);
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 4px solid #00ff99;
    }
    .feedback-incorrect {
        color: #ff6699;
        padding: 1rem;
        background: rgba(255, 102, 153, 0.1);
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 4px solid #ff6699;
    }
    .explanation {
        background: rgba(30, 30, 30, 0.9);
        padding: 1.2rem;
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 3px solid #ffcc00;
        color: #ffffff;
    }

    /* Topic selector */
    .topic-chip {
        display: inline-block;
        background: rgba(0, 136, 204, 0.2);
        color: #00ccff;
        border-radius: 20px;
        padding: 0.4rem 1rem;
        margin: 0.2rem;
        font-size: 0.9rem;
        transition: background 0.3s ease;
    }
    .topic-chip:hover {
        background: rgba(0, 136, 204, 0.4);
    }
    .topic-selector {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 1.5rem;
    }

    /* Score wheel */
    .score-wheel-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 2rem 0;
    }
    .score-wheel {
        width: 220px;
        height: 220px;
        position: relative;
        background: conic-gradient(#00ff99 {score_percentage}%, #ff6699 {score_percentage}% 100%);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: transform 0.3s ease;
    }
    .score-wheel:hover {
        transform: scale(1.05);
    }
    .score-wheel-inner {
        width: 200px;
        height: 200px;
        background: #1a1a1a;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: bold;
    }
    .score-details {
        margin-top: 1rem;
        text-align: center;
        color: #00ccff;
        font-size: 1.1rem;
    }
    .results-list {
        width: 100%;
        margin-top: 2rem;
    }
    .result-item {
        background: rgba(25, 25, 25, 0.95);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid rgba(0, 204, 255, 0.2);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }

    /* Login and Leaderboard */
    .login-container {
        background: rgba(25, 25, 25, 0.95);
        border-radius: 15px;
        padding: 2rem;
        max-width: 450px;
        margin: 3rem auto;
        border: 1px solid rgba(0, 204, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .login-title {
        font-size: 2rem;
        font-weight: 600;
        color: #00ccff;
        text-align: center;
        margin-bottom: 2rem;
    }
    .leaderboard-container {
        background: linear-gradient(135deg, rgba(15, 15, 15, 0.95) 0%, rgba(26, 26, 26, 0.95) 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin-top: 2rem;
        border: 2px solid #00ccff;
        box-shadow: 0 8px 30px rgba(0, 204, 255, 0.3), 0 0 15px rgba(0, 204, 255, 0.5);
        position: relative;
        overflow: hidden;
    }
    .leaderboard-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 204, 255, 0.1) 0%, transparent 70%);
        animation: pulse 10s infinite;
        z-index: 0;
    }
    .leaderboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00ffcc;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
        animation: glow 2s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { text-shadow: 0 0 5px #00ffcc, 0 0 10px #00ffcc; }
        to { text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc, 0 0 30px #00ff99; }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .leaderboard-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 10px;
        z-index: 1;
        position: relative;
    }
    .leaderboard-table th, .leaderboard-table td {
        padding: 1.2rem 1.5rem;
        text-align: center;
        border: none;
        transition: transform 0.3s ease, background 0.3s ease;
        color: #ffffff; /* Unified text color for all table content */
    }
    .leaderboard-table th {
        background: rgba(0, 204, 255, 0.15);
        color: #00ffcc;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 1.1rem;
    }
    .leaderboard-table td {
        background: rgba(30, 30, 30, 0.9);
        color: #ffffff; /* Ensure consistent white text */
        font-weight: 500;
        border-radius: 10px;
    }
    .leaderboard-table tr:hover td {
        transform: scale(1.02);
        background: rgba(0, 204, 255, 0.2);
        color: #ffffff; /* Changed to white for consistency */
    }
    .leaderboard-table td:first-child {
        border-top-left-radius: 10px;
        border-bottom-left-radius: 10px;
    }
    .leaderboard-table td:last-child {
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00ccff, #0077b6);
        color: #ffffff;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: background 0.3s ease, transform 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #00e0ff, #0088cc);
        transform: translateY(-2px);
    }
    .stButton>button:active {
        transform: translateY(0);
    }
    .stButton>button[aria-label="primary"] {
        background: linear-gradient(90deg, #00ff99, #00cc99);
    }
    .stButton>button[aria-label="primary"]:hover {
        background: linear-gradient(90deg, #00ffaa, #00ddaa);
    }

    /* Input fields */
    .stTextInput>div>input, .stTextArea>div>textarea {
        background: rgba(40, 40, 40, 0.9);
        color: #ffffff;
        border: 1px solid rgba(0, 204, 255, 0.3);
        border-radius: 8px;
        padding: 0.75rem;
    }
    .stTextInput>div>input:focus, .stTextArea>div>textarea:focus {
        border-color: #00ccff;
        box-shadow: 0 0 5px rgba(0, 204, 255, 0.5);
    }

    /* File uploader */
    .stFileUploader>div {
        background: rgba(40, 40, 40, 0.9);
        border: 1px solid rgba(0, 204, 255, 0.3);
        border-radius: 10px;
        padding: 1rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 2rem;
        background: rgba(20, 20, 20, 0.95);
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'generator'
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'quiz_topics' not in st.session_state:
    st.session_state.quiz_topics = []
if 'explanations' not in st.session_state:
    st.session_state.explanations = {}
if 'last_interaction' not in st.session_state:
    st.session_state.last_interaction = time.time()

# Login Page
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-container">
        <div class="login-title">Welcome to QuizGen</div>
    """, unsafe_allow_html=True)
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", use_container_width=True, type="primary"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with register_tab:
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input("New Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        if st.button("Register", use_container_width=True, type="primary"):
            if new_password == confirm_password:
                if register_user(new_username, new_password):
                    st.success("Registered successfully! Please login.")
                else:
                    st.error("Username already exists")
            else:
                st.error("Passwords do not match")
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # Header section
    st.markdown("""
    <div class="header">
        <div class="title">📚 QuizGen</div>
        <div class="subtitle">Transforming Education with AI-Powered Quizzes</div>
        <div style="text-align: right; margin-top: 1rem;">
            <span style="color: #00ccff; font-weight: 500;">Welcome, {}</span>
        </div>
    """.format(st.session_state.username), unsafe_allow_html=True)

    # Logout button
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.active_tab = 'generator'
        st.session_state.quiz_data = None
        st.session_state.current_question = 0
        st.session_state.user_answers = {}
        st.session_state.score = 0
        st.session_state.show_results = False
        st.session_state.quiz_topics = []
        st.session_state.explanations = {}
        st.rerun()

    # Navigation tabs
    col1, col2, col3, col4 = st.columns([1,1,1,3])
    with col1:
        if st.button("🧠 Generator", use_container_width=True, 
                     type="primary" if st.session_state.active_tab == 'generator' else "secondary"):
            st.session_state.active_tab = 'generator'
            st.session_state.quiz_data = None
            st.session_state.current_question = 0
            st.session_state.user_answers = {}
            st.session_state.score = 0
            st.session_state.show_results = False
            st.session_state.explanations = {}
    
    with col2:
        if st.button("🏆 Leaderboard", use_container_width=True, 
                     type="primary" if st.session_state.active_tab == 'leaderboard' else "secondary"):
            st.session_state.active_tab = 'leaderboard'
    
    with col3:
        if st.button("ℹ️ About Us", use_container_width=True, 
                     type="primary" if st.session_state.active_tab == 'about' else "secondary"):
            st.session_state.active_tab = 'about'

    # Generator Tab
    if st.session_state.active_tab == 'generator':
        # Features section
        st.markdown("""
        <div class="card">
            <div class="card-title">✨ Key Features</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Multi-Format Support</div>
                <div class="feature-desc">Upload PDF, DOCX, or TXT files with ease</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Lightning Fast</div>
                <div class="feature-desc">Generate quizzes in seconds</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">Advanced AI</div>
                <div class="feature-desc">Powered by state-of-the-art LLMs</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">💯</div>
                <div class="feature-title">Interactive Quizzes</div>
                <div class="feature-desc">Engage with instant feedback and scoring</div>
            </div>
            """, unsafe_allow_html=True)

        # Main content
        st.markdown("""
        <div class="card">
            <div class="card-title">📥 Input Syllabus Content</div>
        </div>
        """, unsafe_allow_html=True)

        # Input options
        input_method = st.radio("Input method:", ("File Upload", "Text Paste"), 
                                horizontal=True, label_visibility="collapsed")

        text = ""
        if input_method == "File Upload":
            st.markdown('<div class="upload-area">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload syllabus file (PDF, DOCX, TXT)", 
                type=["pdf", "docx", "txt"],
                label_visibility="visible"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            if uploaded_file:
                try:
                    text = extract_text(uploaded_file, uploaded_file.type)
                    st.success(f"✅ Successfully extracted text from {uploaded_file.name}")
                    
                    # Extract topics from text
                    with st.spinner("🔍 Identifying topics..."):
                        model = ChatGroq(
                            temperature=0.5,
                            groq_api_key=GROQ_API_KEY,
                            model_name="llama3-70b-8192"
                        )
                        prompt = PromptTemplate.from_template("""
                        Analyze the following syllabus content and extract 5-7 main topics suitable for quiz generation.
                        Return ONLY a JSON array of topic names without any additional text.
                        
                        Syllabus Content:
                        {text}
                        """)
                        chain = prompt | model | StrOutputParser()
                        topics_json = chain.invoke({"text": text})
                        
                        try:
                            st.session_state.quiz_topics = json.loads(topics_json)
                        except:
                            st.session_state.quiz_topics = []
                except Exception as e:
                    st.error(f"Error extracting text: {str(e)}")
                    
        elif input_method == "Text Paste":
            text = st.text_area("Paste Syllabus Content:", 
                                height=200, 
                                placeholder="Paste your syllabus content here...",
                                label_visibility="visible")

        # Quiz configuration
        st.markdown("""
        <div class="card">
            <div class="card-title">⚙️ Quiz Configuration</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1.5])
        with col1:
            st.markdown('<div style="margin-bottom: 10px; font-weight: 500; color: #00ccff;">Quiz Type</div>', unsafe_allow_html=True)
            quiz_type = st.selectbox("Quiz Type", ["MCQ", "True/False", "Fill-in-the-Blank"], label_visibility="collapsed")
            
        with col2:
            st.markdown('<div style="margin-bottom: 10px; font-weight: 500; color: #00ccff;">Number of Questions</div>', unsafe_allow_html=True)
            num_questions = st.slider("Number of Questions", 1, 20, 5, label_visibility="collapsed")
            
        with col3:
            st.markdown('<div class="model-selector">', unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom: 10px; font-weight: 500; color: #00ccff;">AI Model Selection</div>', unsafe_allow_html=True)
            model_choice = st.radio("AI Model", 
                                    ["Llama 3 70B (Recommended)", "Mixtral 8x7B", "Llama 3 8B"],
                                    label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

        # Topic selection
        if st.session_state.quiz_topics:
            st.markdown("""
            <div class="card">
                <div class="card-title">📚 Select Topics</div>
                <div class="topic-selector">
            """, unsafe_allow_html=True)
            
            selected_topics = []
            for topic in st.session_state.quiz_topics:
                if st.checkbox(topic, value=True, key=f"topic_{topic}"):
                    selected_topics.append(topic)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # Add selected topics to context
            if selected_topics:
                text += f"\n\nFocus on these topics: {', '.join(selected_topics)}"

        # Model mapping
        MODELS = {
            "Llama 3 70B (Recommended)": "llama3-70b-8192",
            "Mixtral 8x7B": "mixtral-8x7b-32768",
            "Llama 3 8B": "llama3-8b-8192"
        }

        # Generate quiz button
        st.markdown("</div>", unsafe_allow_html=True) # Close card

        if st.button("✨ Generate Quiz", use_container_width=True, type="primary", key="generate_quiz"):
            if not text.strip():
                st.warning("Please provide syllabus content")
                st.stop()
            
            selected_model = MODELS[model_choice]
            with st.spinner(f"🧠 Generating {num_questions} {quiz_type} questions using {model_choice}..."):
                try:
                    quiz = generate_quiz(text, quiz_type, num_questions, GROQ_API_KEY)
                    st.session_state.quiz = quiz
                    st.session_state.quiz_type = quiz_type
                    st.session_state.num_questions = num_questions
                    st.session_state.model_choice = model_choice
                    
                    # Parse quiz for interactive session
                    if quiz_type == "MCQ":
                        pattern = r"Q(\d+)\.\s*(.*?)\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)\s*Answer:\s*(\w)"
                        matches = re.findall(pattern, quiz, re.DOTALL)
                        
                        quiz_data = []
                        for match in matches:
                            quiz_data.append({
                                "question": match[1].strip(),
                                "options": {
                                    "a": match[2].strip(),
                                    "b": match[3].strip(),
                                    "c": match[4].strip(),
                                    "d": match[5].strip()
                                },
                                "correct": match[6].strip().lower()
                            })
                        st.session_state.quiz_data = quiz_data
                        st.session_state.current_question = 0
                        st.session_state.user_answers = {}
                        st.session_state.score = 0
                        st.session_state.show_results = False
                        st.session_state.explanations = {}
                
                    st.success("✅ Quiz generated successfully!")
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")
                    st.write("💡 If you see model errors, try switching to a different AI model")
                    st.stop()

        # Interactive Quiz Interface
        if st.session_state.quiz_data and st.session_state.quiz_type == "MCQ" and not st.session_state.show_results:
            st.markdown("""
            <div class="card">
                <div class="card-title">📝 Interactive Quiz</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Quiz container
            with st.container():
                st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
                
                total_questions = len(st.session_state.quiz_data)
                score = st.session_state.score
                header_html = f"""
                <div class="quiz-header">
                    <div class="question-counter">Question {st.session_state.current_question + 1}/{total_questions}</div>
                    <div class="score-display">Score: {score}/{total_questions}</div>
                </div>
                """
                st.markdown(header_html, unsafe_allow_html=True)

                # Current question
                question_data = st.session_state.quiz_data[st.session_state.current_question]
                st.markdown(f'<div class="question-text">Q{st.session_state.current_question + 1}. {question_data["question"]}</div>', unsafe_allow_html=True)
                
                # Options - FIXED: Now updates selection correctly
                key = f"question_{st.session_state.current_question}"
                if key in st.session_state:
                    default_index = ord(st.session_state.user_answers.get(st.session_state.current_question, ' ')) - ord('a') 
                    if default_index < 0 or default_index > 3:
                        default_index = None
                else:
                    default_index = None
                    
                options = [
                    f"a) {question_data['options']['a']}",
                    f"b) {question_data['options']['b']}",
                    f"c) {question_data['options']['c']}",
                    f"d) {question_data['options']['d']}"
                ]
                
                user_answer = st.radio(
                    "Select your answer:",
                    options=options,
                    index=default_index,
                    key=key
                )
                
                # Always update answer when selection changes
                if user_answer:
                    answer_char = user_answer[0].lower()
                    st.session_state.user_answers[st.session_state.current_question] = answer_char
                
                # Navigation buttons
                col1, col2, col3 = st.columns([1,1,2])
                with col1:
                    if st.session_state.current_question > 0:
                        if st.button("⬅️ Previous", use_container_width=True):
                            st.session_state.current_question -= 1
                            st.rerun()
                
                with col2:
                    if st.session_state.current_question < len(st.session_state.quiz_data) - 1:
                        if st.button("Next ➡️", use_container_width=True):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                            # Calculate score and generate explanations
                            score = 0
                            # Use faster model for explanations to improve response time
                            model = ChatGroq(
                                temperature=0.7,
                                groq_api_key=GROQ_API_KEY,
                                model_name="llama3-8b-8192"  # Faster model
                            )
                            prompt = PromptTemplate.from_template("""
                            Explain why the correct answer is {correct} for this question:
                            Question: {question}
                            Options:
                            a) {a}
                            b) {b}
                            c) {c}
                            d) {d}
                            
                            Provide a concise 1-2 sentence explanation.
                            """)
                            chain = prompt | model | StrOutputParser()
                            
                            with st.spinner("🧠 Generating explanations..."):
                                for i, q in enumerate(st.session_state.quiz_data):
                                    if i in st.session_state.user_answers and st.session_state.user_answers[i] == q["correct"]:
                                        score += 1
                                    # Generate explanation
                                    explanation = chain.invoke({
                                        "correct": q["correct"],
                                        "question": q["question"],
                                        "a": q["options"]["a"],
                                        "b": q["options"]["b"],
                                        "c": q["options"]["c"],
                                        "d": q["options"]["d"]
                                    })
                                    st.session_state.explanations[i] = explanation
                            
                            st.session_state.score = score
                            save_score(st.session_state.username, score, len(st.session_state.quiz_data))
                            st.session_state.show_results = True
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True) # Close quiz-container
                
            st.markdown("</div>", unsafe_allow_html=True) # Close card

        # Score Wheel and Results Display
        if st.session_state.show_results and st.session_state.quiz_data:
            st.markdown("""
            <div class="card">
                <div class="card-title">🏆 Quiz Results</div>
            </div>
            """, unsafe_allow_html=True)
            
            total_questions = len(st.session_state.quiz_data)
            score_percentage = (st.session_state.score / total_questions) * 100
            score_html = f"""
            <div class="score-wheel-container">
                <div class="score-wheel">
                    <div class="score-wheel-inner">
                        {st.session_state.score}/{total_questions}
                        <div style="font-size: 1rem; font-weight: normal;">{score_percentage:.1f}%</div>
                    </div>
                </div>
                <div class="score-details">
                    <p>You got {st.session_state.score} out of {total_questions} questions correct!</p>
                </div>
            </div>
            """
            st.markdown(score_html.format(score_percentage=score_percentage), unsafe_allow_html=True)

            # Display all questions with feedback and explanations
            st.markdown('<div class="results-list">', unsafe_allow_html=True)
            for i, question in enumerate(st.session_state.quiz_data):
                user_answer = st.session_state.user_answers.get(i, None)
                correct_answer = question['correct']
                is_correct = user_answer == correct_answer
                
                feedback_html = (
                    f'<div class="feedback-correct">✓ Correct! Well done.</div>'
                    if is_correct else
                    f'<div class="feedback-incorrect">✗ Incorrect. The correct answer is <strong>{correct_answer.upper()}) {question['options'][correct_answer]}</strong></div>'
                )
                
                st.markdown(f"""
                <div class="result-item">
                    <h4>Q{i+1}. {question['question']}</h4>
                    <p>Your answer: {user_answer.upper() if user_answer else 'Not answered'}) {question['options'][user_answer] if user_answer else ''}</p>
                    {feedback_html}
                    <div class="explanation">💡 {st.session_state.explanations.get(i, 'No explanation available.')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True) # Close results-list

            # Generate More Quiz button
            if st.button("✨ Generate More Quiz", use_container_width=True, type="primary", key="generate_more_quiz"):
                st.session_state.quiz_data = None
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.session_state.score = 0
                st.session_state.show_results = False
                st.session_state.explanations = {}
                st.session_state.active_tab = 'generator'
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True) # Close card

        # Display results (non-interactive)
        if "quiz" in st.session_state and not st.session_state.quiz_data:
            st.markdown("""
            <div class="card">
                 <div class="card-title">📝 Generated Quiz</div>
            </div>
            """, unsafe_allow_html=True)
            st.text_area(
                label="Review your quiz",
                value=st.session_state.quiz,
                height=400,
                key="quiz_display_area"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if "quiz" in st.session_state:
            st.markdown("""
                <div class="card">
                    <div class="card-title">💾 Export Quiz</div>
                    <div style="display: flex; gap: 20px; margin-top: 1.5rem;">
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download as TXT",
                    data=st.session_state.quiz,
                    file_name="generated_quiz.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                if st.session_state.quiz_type == "MCQ":
                    try:
                        df = pd.DataFrame(st.session_state.quiz_data)
                        # Reformat the dataframe for a clean CSV
                        df_export = pd.DataFrame({
                            "Question": df["question"],
                            "Option A": df["options"].apply(lambda x: x.get("a")),
                            "Option B": df["options"].apply(lambda x: x.get("b")),
                            "Option C": df["options"].apply(lambda x: x.get("c")),
                            "Option D": df["options"].apply(lambda x: x.get("d")),
                            "Correct Answer": df["correct"]
                        })
                        csv = df_export.to_csv(index=False).encode('utf-8')
                        
                        st.download_button(
                            label="📊 Download as CSV",
                            data=csv,
                            file_name="generated_quiz.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.warning(f"Could not convert to CSV: {e}")
            
            st.markdown("</div></div>", unsafe_allow_html=True) # Close card

    # Leaderboard Tab
    elif st.session_state.active_tab == 'leaderboard':
        st.markdown("""
        <div class="card">
            <div class="card-title">🏆 Leaderboard</div>
        </div>
        """, unsafe_allow_html=True)
        
        leaderboard_data = get_leaderboard()
        if leaderboard_data:
            st.markdown('<div class="leaderboard-container">', unsafe_allow_html=True)
            st.markdown('<div class="leaderboard-title animate__animated animate__fadeIn">Leaderboard</div>', unsafe_allow_html=True)
            
            # Fallback DataFrame display with epic styling
            df = pd.DataFrame(
                leaderboard_data,
                columns=["Username", "Score (%)", "Correct", "Total Questions", "Date", "Attempts"]
            )
            df.insert(0, "Rank", range(1, len(df) + 1))
            styled_df = df.style.set_properties(**{
                'text-align': 'center',
                'background-color': 'rgba(30, 30, 30, 0.9)',
                'color': '#ffffff', 
                'border': 'none',
                'padding': '1.2rem 1.5rem',
                'border-radius': '10px',
                'transition': 'all 0.3s ease'
            }).set_table_styles([
                {'selector': 'th',
                 'props': [
                     ('background-color', 'rgba(0, 204, 255, 0.15)'),
                     ('color', '#00ffcc'),
                     ('font-weight', '600'),
                     ('text-transform', 'uppercase'),
                     ('letter-spacing', '1px'),
                     ('font-size', '1.1rem'),
                     ('padding', '1.2rem 1.5rem'),
                     ('text-align', 'center')
                 ]}
            ]).set_table_attributes('class="leaderboard-table"')

            # Apply rank-specific styling using apply with CSS styles, ensuring white text
            def highlight_ranks(row):
                rank = row['Rank']
                styles = [''] * len(row)
                if rank == 1:
                    styles = ['background: linear-gradient(45deg, #ffd700, #ffec80); color: #ffffff; font-weight: 700; animation: bounce 0.5s ease-out'] * len(row)
                elif rank == 2:
                    styles = ['background: linear-gradient(45deg, #c0c0c0, #e0e0e0); color: #ffffff; font-weight: 600'] * len(row)
                elif rank == 3:
                    styles = ['background: linear-gradient(45deg, #cd7f32, #d9a066); color: #ffffff; font-weight: 600'] * len(row)
                return styles

            styled_df = styled_df.apply(highlight_ranks, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No scores available yet. Take a quiz to become a champion!")

    # About Us Tab
    elif st.session_state.active_tab == 'about':
        st.markdown("""
        <div class="card">
            <div class="card-title">🚀 About QuizGen</div>
            <p style="font-size: 1.1rem; line-height: 1.6;">
                QuizGen is an innovative platform designed to revolutionize the educational experience for teachers and students. By harnessing cutting-edge Large Language Models (LLMs) through the Groq API, QuizGen transforms static syllabus content into engaging, interactive quizzes that enhance learning and retention.
            </p>
            <div class="card-title" style="margin-top: 2rem;">🛠️ Technology Stack</div>
            <ul style="font-size: 1rem; line-height: 1.8;">
                <li><strong>Frontend:</strong> Streamlit for a seamless and intuitive user interface</li>
                <li><strong>AI/ML:</strong> LangChain for advanced prompt engineering and model interaction</li>
                <li><strong>Core Engine:</strong> Groq API for high-speed LLM inference (Llama 3, Mixtral)</li>
                <li><strong>File Processing:</strong> PyPDF2 and python-docx for versatile document handling</li>
                <li><strong>Database:</strong> SQLite for secure user authentication and score tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <p>Developed with ❤️ for College Project | Powered by Streamlit, LangChain, and Groq API</p>
        <p style="margin-top: 10px; font-size: 0.85rem; opacity: 0.7;">© 2025 QuizGen | AI-Powered Educational Platform</p>
    </div>
    """, unsafe_allow_html=True)