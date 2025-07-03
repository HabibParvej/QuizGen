from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def generate_quiz(text, quiz_type, num_questions, groq_api_key):
    """Generate quiz questions using Groq API"""
    # Define prompt templates for different quiz types
    templates = {
        "MCQ": """
        Generate {num_questions} multiple choice questions based EXCLUSIVELY on the following syllabus content.
        Each question must have 4 options with ONE correct answer. Use this format:
        
        Q1. [Question]
        a) [Option A]
        b) [Option B]
        c) [Option C]
        d) [Option D]
        Answer: [Correct Option Letter]
        
        Syllabus Content:
        {text}
        """,
        
        "True/False": """
        Generate {num_questions} True/False questions based EXCLUSIVELY on the following syllabus content.
        Use this format:
        
        Q1. [Statement]
        Answer: True/False
        
        Syllabus Content:
        {text}
        """,
        
        "Fill-in-the-Blank": """
        Generate {num_questions} Fill-in-the-Blank questions based EXCLUSIVELY on the following syllabus content.
        Use ____ to represent blanks. Use this format:
        
        Q1. [Sentence with blank]
        Answer: [Correct Answer]
        
        Syllabus Content:
        {text}
        """
    }
    
    # Configure Groq client with latest models
    model = ChatGroq(
        temperature=0.7,
        groq_api_key=groq_api_key,
        # Use latest Mixtral or Llama 3 models
        model_name="llama3-70b-8192"  # Alternative: "mixtral-8x7b-32768" if available
    )
    
    # Create and execute the chain
    prompt = PromptTemplate.from_template(templates[quiz_type])
    chain = (
        RunnablePassthrough.assign(num_questions=lambda _: num_questions)
        | prompt
        | model
        | StrOutputParser()
    )
    
    return chain.invoke({"text": text})