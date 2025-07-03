import streamlit as st
from utils.extract_text import extract_text
from utils.quiz_generator import generate_quiz
from dotenv import load_dotenv
import os
import pandas as pd
import re

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Page configuration
st.set_page_config(
    page_title="📚Quiz Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for black theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Roboto+Mono:wght@300;400;500&display=swap');
    
    * {
        font-family: 'Montserrat', sans-serif;
    }
    
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    
    .header {
        background: linear-gradient(90deg, #111111 0%, #222222 100%);
        color: white;
        padding: 3rem 1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.4);
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
        border-bottom: 2px solid #00ccff;
    }
    
    .title {
        font-size: 3.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #00ccff, #00ffcc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        font-size: 1.3rem;
        text-align: center;
        opacity: 0.85;
        margin-bottom: 1rem;
        font-weight: 300;
        color: #cccccc;
    }
    
    .card {
        background: rgba(20, 20, 20, 0.9);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 1.8rem;
        border: 1px solid rgba(0, 204, 255, 0.2);
    }
    
    .card-title {
        color: #00ccff;
        font-weight: 600;
        font-size: 1.6rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 2px solid #0088cc;
        padding-bottom: 0.8rem;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #0088cc, #00ccff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.9rem 1.8rem;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        background: linear-gradient(90deg, #00aaff, #00ffff);
    }
    
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #00ccff, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    .feature-box {
        background: rgba(0, 136, 204, 0.15);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.4s;
        border: 1px solid rgba(0, 204, 255, 0.2);
        height: 100%;
    }
    
    .feature-box:hover {
        transform: translateY(-8px);
        background: rgba(0, 136, 204, 0.25);
        box-shadow: 0 10px 25px rgba(0, 204, 255, 0.2);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #00ccff;
    }
    
    .feature-title {
        font-weight: 600;
        margin-bottom: 0.8rem;
        color: #ffffff;
        font-size: 1.2rem;
    }
    
    .feature-desc {
        color: #aaaaaa;
        font-size: 0.95rem;
    }
    
    .tech-badge {
        display: inline-block;
        background: rgba(0, 136, 204, 0.2);
        color: #00ccff;
        border-radius: 20px;
        padding: 0.4rem 1.2rem;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        border: 1px solid rgba(0, 204, 255, 0.3);
    }
    
    .quiz-card {
        background: rgba(15, 15, 15, 0.9);
        border-left: 4px solid #00ccff;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        transition: all 0.3s;
    }
    
    .quiz-card:hover {
        transform: translateX(5px);
        border-left: 4px solid #00ffcc;
    }
    
    .question {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #ffffff;
        font-size: 1.2rem;
        line-height: 1.5;
    }
    
    .option {
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.7rem;
        border-radius: 10px;
        background: rgba(0, 136, 204, 0.15);
        border: 1px solid rgba(0, 204, 255, 0.2);
        transition: all 0.2s;
    }
    
    .option:hover {
        background: rgba(0, 136, 204, 0.25);
    }
    
    .correct {
        background: rgba(0, 204, 102, 0.2);
        border-left: 4px solid #00cc66;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #aaaaaa;
        font-size: 0.95rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(0, 204, 255, 0.2);
    }
    
    .model-selector {
        background: rgba(20, 20, 20, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        border: 1px solid rgba(0, 204, 255, 0.2);
    }
    
    .upload-area {
        border: 2px dashed #00ccff;
        border-radius: 15px;
        padding: 2.5rem;
        text-align: center;
        background: rgba(0, 136, 204, 0.08);
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .upload-area:hover {
        background: rgba(0, 136, 204, 0.15);
        border: 2px dashed #00ffcc;
    }
    
    .stRadio > div {
        background: rgba(20, 20, 20, 0.9);
        border-radius: 12px;
        padding: 0.5rem;
        border: 1px solid rgba(0, 204, 255, 0.2);
    }
    
    .stRadio > div > label > div:first-child {
        color: #ffffff !important;
    }
    
    .stRadio > div > label > div:last-child {
        color: #aaaaaa !important;
    }
    
    .stSlider > div > div > div > div {
        background: #00ccff !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(20, 20, 20, 0.9) !important;
        border: 1px solid rgba(0, 204, 255, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(20, 20, 20, 0.9) !important;
        border: 1px solid rgba(0, 204, 255, 0.3) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stFileUploader > div > div {
        background: transparent !important;
        border: none !important;
    }
    
    .stAlert {
        border-radius: 12px !important;
    }
    
    .tab-button {
        background: transparent;
        border: none;
        color: #aaaaaa;
        font-size: 1.1rem;
        padding: 0.5rem 1.5rem;
        cursor: pointer;
        transition: all 0.3s;
        border-bottom: 2px solid transparent;
    }
    
    .tab-button.active {
        color: #00ccff;
        border-bottom: 2px solid #00ccff;
    }
    
    .tab-content {
        display: none;
    }
    
    .tab-content.active {
        display: block;
    }
    
    .about-content {
        background: rgba(15, 15, 15, 0.9);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(0, 204, 255, 0.2);
    }
    
    .team-member {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: rgba(20, 20, 20, 0.7);
        border-radius: 10px;
        border-left: 3px solid #00ccff;
    }
    
    .member-info {
        margin-left: 1.5rem;
    }
    
    .member-name {
        font-weight: 600;
        font-size: 1.2rem;
        color: #00ccff;
        margin-bottom: 0.3rem;
    }
    
    .member-role {
        color: #aaaaaa;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0px rgba(0, 204, 255, 0.6); }
        100% { box-shadow: 0 0 0 15px rgba(0, 204, 255, 0); }
    }
    
    .tech-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 15px;
        margin-top: 1rem;
    }
    
    .tech-item {
        background: rgba(0, 136, 204, 0.15);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(0, 204, 255, 0.2);
        transition: all 0.3s;
    }
    
    .tech-item:hover {
        transform: translateY(-5px);
        background: rgba(0, 136, 204, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for active tab
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'generator'

# Header section
st.markdown("""
<div class="header">
    <div class="title">📚 QUIZGEN</div>
    <div class="subtitle">Transform Educational Content into Interactive Quizzes with AI</div>
</div>
""", unsafe_allow_html=True)

# Navigation tabs
col1, col2, col3 = st.columns([1,1,6])
with col1:
    if st.button("🧠 Generator", use_container_width=True, 
                 type="primary" if st.session_state.active_tab == 'generator' else "secondary"):
        st.session_state.active_tab = 'generator'
        
with col2:
    if st.button("ℹ️ About Us", use_container_width=True, 
                 type="primary" if st.session_state.active_tab == 'about' else "secondary"):
        st.session_state.active_tab = 'about'

# Generator Tab
if st.session_state.active_tab == 'generator':
    # Features section
    st.markdown("""
    <div class="card-title" style="padding-left: 10px; margin-top: 10px;">✨ KEY FEATURES</div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Multi-Format Support</div>
            <div class="feature-desc">Process PDF, DOCX, and TXT files</div>
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
            <div class="feature-desc">Uses state-of-the-art language models</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">💾</div>
            <div class="feature-title">Export Options</div>
            <div class="feature-desc">Download as TXT or CSV</div>
        </div>
        """, unsafe_allow_html=True)

    # Main content
    st.markdown("""
    <div class="card">
        <div class="card-title">📥 INPUT SYLLABUS CONTENT</div>
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
        <div class="card-title">⚙️ QUIZ CONFIGURATION</div>
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

    # Model mapping
    MODELS = {
        "Llama 3 70B (Recommended)": "llama3-70b-8192",
        "Mixtral 8x7B": "mixtral-8x7b-32768",
        "Llama 3 8B": "llama3-8b-8192"
    }

    # Generate quiz button
    st.markdown("</div>", unsafe_allow_html=True)  # Close card

    if st.button("✨ GENERATE QUIZ", use_container_width=True, type="primary", key="generate_quiz"):
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
                st.success("✅ Quiz generated successfully!")
            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")
                st.write("💡 If you see model errors, try switching to a different AI model")
                st.stop()

    # Display results
    if "quiz" in st.session_state:
        st.markdown("""
        <div class="card">
            <div class="card-title">📝 GENERATED QUIZ</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem; background: rgba(30, 30, 30, 0.9); padding: 1rem; border-radius: 10px;">
                <div><b>Quiz Type:</b> {}</div>
                <div><b>Questions:</b> {}</div>
                <div><b>Model:</b> {}</div>
            </div>
        """.format(st.session_state.quiz_type, 
                  st.session_state.num_questions, 
                  st.session_state.model_choice), unsafe_allow_html=True)
        
        # Format and display quiz
        if st.session_state.quiz_type == "MCQ":
            pattern = r"Q(\d+)\.\s*(.*?)\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)\s*Answer:\s*(\w)"
            matches = re.findall(pattern, st.session_state.quiz, re.DOTALL)
            
            for match in matches:
                q_num = match[0]
                question = match[1].strip()
                options = [opt.strip() for opt in match[2:6]]
                answer = match[6].strip().lower()
                
                st.markdown(f"""
                <div class="quiz-card">
                    <div class="question">Q{q_num}. {question}</div>
                    <div class="option {'correct' if answer == 'a' else ''}">a) {options[0]}</div>
                    <div class="option {'correct' if answer == 'b' else ''}">b) {options[1]}</div>
                    <div class="option {'correct' if answer == 'c' else ''}">c) {options[2]}</div>
                    <div class="option {'correct' if answer == 'd' else ''}">d) {options[3]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(st.session_state.quiz)
        
        # Download options
        st.markdown("""
            <div class="divider"></div>
            <div class="card-title">💾 EXPORT QUIZ</div>
            <div style="display: flex; gap: 20px; margin-top: 1.5rem;">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state.quiz,
                file_name="generated_quiz.txt",
                mime="text/plain"
            )
        
        with col2:
            if st.session_state.quiz_type == "MCQ":
                try:
                    questions = []
                    pattern = r"Q(\d+)\.\s*(.*?)\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)\s*Answer:\s*(\w)"
                    matches = re.findall(pattern, st.session_state.quiz, re.DOTALL)
                    
                    for match in matches:
                        questions.append({
                            "Question": match[1].strip(),
                            "Option A": match[2].strip(),
                            "Option B": match[3].strip(),
                            "Option C": match[4].strip(),
                            "Option D": match[5].strip(),
                            "Correct Answer": match[6].strip()
                        })
                    
                    df = pd.DataFrame(questions)
                    csv = df.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="📊 Download as CSV",
                        data=csv,
                        file_name="generated_quiz.csv",
                        mime="text/csv"
                    )
                except:
                    st.warning("Could not convert to CSV format")
        
        st.markdown("</div></div>", unsafe_allow_html=True)  # Close card

# About Us Tab
elif st.session_state.active_tab == 'about':
    st.markdown("""
    <div class="about-content">
        <div class="card-title">🚀 ABOUT THE PROJECT</div>
    """, unsafe_allow_html=True)
    
    st.write("""
    The Syllabus-to-Quiz Generator revolutionizes the way educators and students create assessments from course materials. 
    Leveraging cutting-edge AI technology, this application transforms syllabus documents into interactive quizzes in seconds. 
    Designed with simplicity and efficiency in mind, it supports multiple file formats and provides various quiz types to suit 
    different educational needs.
    """)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚡ TECHNICAL STACK</div>', unsafe_allow_html=True)
    
    # Tech stack grid
    tech_stack = [
        "Streamlit", "LangChain", "Groq API", "Mistral AI", 
        "Llama 3", "Python", "PDF Parsing", "DOCX Parsing", 
        "NLP", "Machine Learning"
    ]
    
    cols = st.columns(4)
    for i, tech in enumerate(tech_stack):
        with cols[i % 4]:
            st.markdown(f'<div class="tech-item">{tech}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📬 CONTACT US</div>', unsafe_allow_html=True)
    
    st.write("For inquiries, suggestions, or support, please contact us at:")
    st.markdown('<div style="color: #00ccff; font-size: 1.2rem; margin-top: 10px;">contact@quizgenerator.edu</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Developed with ❤️ for College Project | Using Streamlit, LangChain, and Groq API</p>
    <p style="margin-top: 10px; font-size: 0.85rem; opacity: 0.7;">© 2023 Syllabus-to-Quiz Generator | AI-Powered Educational Tool</p>
</div>
""", unsafe_allow_html=True)