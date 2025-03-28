import streamlit as st
import PyPDF2
import docx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini model setup
gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def analyze_resume(text):
    prompt = f"""Analyze this resume and provide:
    1. **Strengths** 
    2. **Areas of Improvement** 
    3. **ATS Optimization Tips**
    4. **Score out of 100** 
    5. **Formatting Tips** 
    6. **Examples of Strong Resumes** 
    7. **References for Resume Writing** 
    8. **Career Recommendations**
     Resume Text: {text}"""

    message=[HumanMessage(content=prompt)]
    response = gemini.invoke(message)
    suggestions= response.content if hasattr(response, 'content') else str(response)


     # Extracting Score and Formatting Tips
    score_section = "Score not found"
    formatting_tips = "Formatting tips not found"
    
    try:
        score_section = suggestions.split('Score out of 100:')[1].split('\n')[0].strip()
    except IndexError:
        pass
    
    try:
        formatting_tips = suggestions.split('Formatting Tips:')[1].split('\n')[0].strip()
    except IndexError:
        pass
    
    return suggestions, score_section, formatting_tips


def download_report(report):
    file_path = "Resume_Analysis_Report.txt"

    with open(file_path, "w") as f:
        f.write(report)
    return file_path

def main():
    st.title("AI-Powered Resume Analyzer")
    st.write("Upload your resume and get AI-driven suggestions!")
    
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        st.info("File uploaded successfully!")
        
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)
        
        if st.button("Analyze"):
            with st.spinner("Analyzing... Please wait"):
                suggestions, score_section, formatting_tips = analyze_resume(resume_text)
                st.success("Analysis Complete!")

             

                

                st.subheader("📝 Full Analysis Report")
                st.markdown(f"<div style='font-size:18px; font-weight: bold;'>{suggestions}</div>", unsafe_allow_html=True)


                 # Download button
                report_file = download_report(suggestions)
                if os.path.exists(report_file):
                    with open(report_file, "rb") as file:
                        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                        st.download_button(label="Download Report", data=file, file_name="Resume_Analysis_Report.txt", mime="text/plain")
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("Failed to generate report file.")

if __name__ == "__main__":
    main()
