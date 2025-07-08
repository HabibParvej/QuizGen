
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_quiz(text, quiz_type, num_questions, api_key):
    """
    Generates a quiz based on the provided text, quiz type, and number of questions.
    
    Args:
        text (str): Input text to base the quiz on
        quiz_type (str): Type of quiz (MCQ, True/False, Fill-in-the-Blank)
        num_questions (int): Number of questions to generate
        api_key (str): Groq API key
    
    Returns:
        str: Generated quiz as a formatted string
    """
    model = ChatGroq(
        temperature=0.7,
        groq_api_key=api_key,
        model_name="llama3-70b-8192"
    )
    
    if quiz_type == "MCQ":
        prompt_template = """
        Using the following syllabus content, generate {num_questions} multiple-choice questions (MCQs) with 4 options each (a, b, c, d) and specify the correct answer.
        Each question should be relevant to the content and formatted as follows:
        
        Q1. [Question]
        a) [Option 1]
        b) [Option 2]
        c) [Option 3]
        d) [Option 4]
        Answer: [Correct option letter]
        
        Syllabus Content:
        {text}
        """
    elif quiz_type == "True/False":
        prompt_template = """
        Using the following syllabus content, generate {num_questions} true/false questions.
        Each question should be relevant to the content and formatted as follows:
        
        Q1. [Statement]
        Answer: [True/False]
        
        Syllabus Content:
        {text}
        """
    elif quiz_type == "Fill-in-the-Blank":
        prompt_template = """
        Using the following syllabus content, generate {num_questions} fill-in-the-blank questions.
        Each question should be relevant to the content and formatted as follows:
        
        Q1. [Sentence with ____ for the blank]
        Answer: [Correct word/phrase]
        
        Syllabus Content:
        {text}
        """
    else:
        raise ValueError("Unsupported quiz type")
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | model | StrOutputParser()
    
    try:
        quiz = chain.invoke({
            "text": text,
            "num_questions": num_questions
        })
        return quiz
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")
