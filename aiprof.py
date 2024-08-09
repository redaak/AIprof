import streamlit as st
import fitz  # PyMuPDF
import requests
import json
import io

# Set up API credentials
api_key = st.secrets["api"]["key"]
base_url = "https://integrate.api.nvidia.com/v1"

def extract_text_from_pdf(uploaded_file):
    if uploaded_file.type != "application/pdf":
        st.error("Please upload a PDF file.")
        return ""

    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    
    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        text += page.get_text()
    
    return text

def generate_quiz(file_content, difficulty, question_type):
    prompt = f"""
    Create quiz questions based on the following content. 
    The difficulty level is {difficulty}. 
    The type of quiz question is {question_type}.

    Content:
    {file_content}
    """

    response = requests.post(
        url=f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta/llama-3.1-405b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that creates quiz questions."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500
        }
    )

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No quiz generated.")
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit app layout
st.set_page_config(page_title="Course Quiz Generator", layout="wide")

st.title("📚 Course Quiz Generator")
st.markdown("Upload your course PDF, specify quiz details, and generate quiz questions.")

# Upload section
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    file_content = extract_text_from_pdf(uploaded_file)
    if file_content:
        st.write("**Extracted Text:**")
        st.text_area("Text Content", value=file_content, height=300)

        # Quiz generation inputs
        st.sidebar.header("Quiz Details")
        difficulty = st.sidebar.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
        question_type = st.sidebar.selectbox("Select Question Type", ["Direct", "Case Scenario", "MCQ", "Essay"])

        if st.sidebar.button("Generate Quiz"):
            with st.spinner('Generating quiz...'):
                quiz_result = generate_quiz(file_content, difficulty, question_type)

            st.markdown("### Generated Quiz Questions")
            st.text_area("Quiz Questions", value=quiz_result, height=300)

            # Button to show/hide answers
            if st.button("Show Answers"):
                # Generate answers (mocked here for demonstration purposes)
                # You need to replace this with actual API call or logic to generate answers
                answers = "These are the answers to the quiz questions."
                st.text_area("Quiz Answers", value=answers, height=300)

else:
    st.markdown("_Please upload a PDF file to proceed._")
