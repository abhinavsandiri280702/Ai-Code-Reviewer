# ai_reviewer.py
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

# ADDED runtime_results to the parameters
def generate_review(code, language, static_analysis_results, runtime_results):
    prompt = f"""
    You are an expert Senior Software Engineer reviewing {language} code.
    
    Static Analyzer Output:
    {static_analysis_results}
    
    Code Execution/Runtime Output:
    {runtime_results}
    
    Source Code:
    ```
    {code}
    ```
    
    Provide a comprehensive code review in Markdown format:
    1. Overall Code Quality Summary.
    2. Explanation of the errors/output from the execution and static analysis.
    3. Security vulnerabilities or logical bugs.
    4. Refactored version of the code.
    """

    response = client.chat.completions.create(
        model=MODEL, 
        messages=[
            {"role": "system", "content": "You are a strict but helpful code reviewer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

def chat_with_code(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.5
    )
    return response.choices[0].message.content