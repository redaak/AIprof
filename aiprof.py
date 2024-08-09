import streamlit as st
import requests
import fitz  # PyMuPDF for PDF extraction
import re

# Set up NVIDIA API
api_key = st.secrets["api"]["key"]
base_url = "https://integrate.api.nvidia.com/v1"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(pdf_file) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def generate_quiz(file_content, difficulty, question_type):
    prompt = f"""
    Generate quiz questions from the following course material with difficulty level {difficulty} and question type {question_type}. Provide questions and answers. 

    Course Material:
    {file_content}
    """
    
    payload = {
        "model": "nvidia/llama-3.1-405b-instruct",  # Replace with the appropriate NVIDIA model
        "prompt": prompt,
        "max_tokens": 1500
    }
    
    response = requests.post(f"{base_url}/generate", headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("text", "").strip()
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return ""

def main():
    st.set_page_config(page_title="Course Quiz Generator", layout="wide")
    st.title("📚 Course Quiz Generator")

    st.markdown("Upload your slides or PDF file and generate quiz questions with the desired difficulty and type.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        file_content = extract_text_from_pdf(uploaded_file)
        st.write("**File Uploaded:**", uploaded_file.name)

        difficulty = st.selectbox("Select Quiz Difficulty", ["Easy", "Medium", "Hard"])
        question_type = st.selectbox("Select Question Type", ["Direct", "Case Scenario", "MCQ", "Essay"])

        if st.button("Generate Quiz"):
            with st.spinner('Generating quiz...'):
                quiz_result = generate_quiz(file_content, difficulty, question_type)

            if quiz_result:
                # Display quiz questions
                st.markdown("### Quiz Questions")

                questions = re.split(r'\n\n+', quiz_result)
                answers = []

                for i, question in enumerate(questions):
                    if i % 2 == 0:
                        st.subheader(f"Question {i//2 + 1}")
                        st.write(question)
                    else:
                        answers.append(question)
                        
                if answers:
                    # Button to reveal answers
                    if st.button("Show Answers"):
                        st.markdown("### Quiz Answers")
                        for i, answer in enumerate(answers):
                            st.write(f"Answer {i + 1}: {answer}")

if __name__ == "__main__":
    main()
