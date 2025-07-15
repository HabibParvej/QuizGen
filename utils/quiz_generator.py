
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_quiz(text, quiz_type, num_questions, api_key):
    model = ChatGroq(
        temperature=0.2,  # Lowered for stricter instruction following
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
        Using the following syllabus content, generate exactly {num_questions} fill-in-the-blank questions.
        Each question should be relevant to the content and formatted as follows:
        
        Q[number]. [Sentence with ____ for the blank]
        Answer: [Correct word/phrase]
        
        Where [number] is the question number starting from 1 up to {num_questions}.
        Ensure that all {num_questions} questions are generated and included in the output.
        
        Syllabus Content:
        {text}
        """
    else:
        raise ValueError("Unsupported quiz type")
    
    prompt = PromptTemplate.from_template(prompt_template)
    # Debug: Print the prompt to verify
    print(prompt.format(text=text, num_questions=num_questions))
    chain = prompt | model | StrOutputParser()
    
    try:
        quiz = chain.invoke({
            "text": text,
            "num_questions": num_questions
        })
        return quiz
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")