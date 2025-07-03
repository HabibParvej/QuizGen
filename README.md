
# 📚 QuizGen - Syllabus to Quiz Generator

QuizGen is an AI-powered web application that transforms syllabus content into interactive quizzes using advanced language models. Built with **Streamlit** and **LangChain**, it enables educators and learners to generate custom quizzes from PDF, DOCX, or TXT syllabus documents in seconds.

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app/)
![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![QuizGen Screenshot](https://via.placeholder.com/800x400.png?text=QuizGen+Screenshot)

---

## 🌟 Features

- 📄 **Multi-Format Support**: Accepts PDF, DOCX, and TXT files
- 🤖 **AI-Powered Quiz Generation**: Uses Groq API with Mistral and Llama 3 models
- 🎯 **Customizable Quiz Types**: MCQs, True/False, Fill-in-the-Blanks
- 📥 **Export Options**: Download quiz as `.txt` or `.csv` (MCQs)
- 🌑 **Sleek Dark UI**: Built with a modern, minimal look
- ⚡ **Fast & Efficient**: Generate quizzes in seconds

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.9 or above
- Groq API key (Get it for free from [console.groq.com](https://console.groq.com/))

### 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/QuizGen.git
cd QuizGen

# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 🔐 Set up API Key

Create a `.env` file in the project root and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### ▶️ Run the App

```bash
streamlit run app.py
```

Visit the app at: [http://localhost:8501](http://localhost:8501)

---

## 🧠 Technology Stack

**Frontend:**
- Streamlit
- CSS3

**Backend:**
- Python
- LangChain
- Groq API (Mistral, Llama3)

**Text Processing:**
- `pdfplumber` (PDF)
- `python-docx` (DOCX)
- Built-in string processing (TXT)

**Environment:**
- `python-dotenv`

---

## 📁 Project Structure

```
QuizGen/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Dependency list
├── .env                    # API key config
├── .gitignore
├── README.md
└── utils/
    ├── extract_text.py     # Handles file text extraction
    └── quiz_generator.py   # Quiz generation logic using LangChain + Groq
```

---

## 📝 How to Use

1. **Upload Syllabus**
   - Choose from PDF, DOCX, or TXT
   - Or paste text manually

2. **Select Options**
   - Quiz Type: MCQ / True-False / Fill-in-the-Blank
   - Number of Questions (1–20)
   - AI Model: Mistral / Llama3 (70B recommended)

3. **Generate Quiz**
   - Click the “Generate Quiz” button
   - View AI-generated questions

4. **Export**
   - Download as `.txt` or `.csv` (MCQ only)

---

## 🌐 Live Demo

🔗 [Try QuizGen Now](https://your-app-url.streamlit.app/)  
_(Replace with your actual deployed app URL)_

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the project
2. Create your feature branch:  
   `git checkout -b feature/AmazingFeature`
3. Commit your changes:  
   `git commit -m 'Add some AmazingFeature'`
4. Push to the branch:  
   `git push origin feature/AmazingFeature`
5. Open a Pull Request 🚀

---

## 📜 License

Distributed under the **MIT License**.  
See [`LICENSE`](https://opensource.org/licenses/MIT) for more details.

---

## 📧 Contact

**Habib Parvej**  
📧 habibparvej777@gmail.com 
🔗 [GitHub](https://github.com/HabibPArvej)

Project Repository: [https://github.com/yourusername/QuizGen](https://github.com/HabibParvej/QuizGen)

---

> *This project was built as part of a college-level application integrating AI tools into education for rapid learning content generation.*
