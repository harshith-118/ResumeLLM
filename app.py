import streamlit as st
import os
import tempfile
import spacy
import json
from PyPDF2 import PdfReader
import docx
from dotenv import load_dotenv
import google.generativeai as genai
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Helper functions for text extraction
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return None

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        text = "\n".join(para.text for para in doc.paragraphs)
        return text
    except Exception as e:
        return None

def get_gemini_response(input_text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(input_text)
    return response.text if response else None

# Analyze text function
def analyze_text(resume_text, job_description):
    input_prompt = f"""
    Act as a highly skilled ATS expert. Evaluate the resume against the provided job description.
    Suggest areas of improvement and assign a percentage match. Identify missing keywords and provide actionable recommendations. Make sure to answer it in english.
    Format the response as:
    {{
        "JD_Match": "Percentage",
        "MissingKeywords": [],
        "Profile_Summary": "",
        "Enhancements_to_be_done": []
    }}
    Resume: {resume_text}
    Job Description: {job_description}
    """
    response = get_gemini_response(input_prompt)
    return response

def clean_input_string(input_string):
    """
    Remove or escape any invalid control characters from the input string,
    and ensure proper JSON formatting (keys enclosed in double quotes).
    """
    # Ensure the keys are properly enclosed in double quotes
    # This uses a regex to match unquoted keys and enclose them in double quotes
    input_string = re.sub(r'(\b\w+\b)(?=:)', r'"\1"', input_string)
    
    # Remove any control characters that might cause issues in JSON parsing
    cleaned_string = re.sub(r'[\x00-\x1f\x7f]', '', input_string)
    return cleaned_string

def process_feedback(response_text):
    # Clean the input string to remove any invalid control characters
    cleaned_response = clean_input_string(response_text)

    try:
        # Parse the cleaned string into a dictionary
        response_dict = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse the response text. Error: {str(e)}"}
    
    # Extract the relevant fields from the parsed JSON
    result_json = {
        "JD_Match": response_dict.get("JD_Match", ""),
        "MissingKeywords": response_dict.get("MissingKeywords", []),
        "Profile_Summary": response_dict.get("Profile_Summary", ""),
        "Enhancements_to_be_done": response_dict.get("Enhancements_to_be_done", [])  # Split the enhancements based on line breaks
    }

    return result_json

# Main Streamlit App
def main():
    st.title("Resume Analyzer with Enhanced ATS Feedback")
    st.write("Upload a resume and paste the job description to get a detailed analysis and actionable recommendations.")

    # Input fields
    job_description = st.text_area("Paste Job Description", placeholder="Enter job description...", height=150)
    uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file and job_description:
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.getvalue())
        temp_file.close()

        # Extract text based on file type
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            resume_text = extract_text_from_pdf(temp_file.name)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(temp_file.name)
        elif file_type == "text/plain":
            resume_text = uploaded_file.getvalue().decode("utf-8")
        else:
            st.error("Unsupported file type.")
            return

        # Analyze resume if text extraction succeeds
        if resume_text:
            st.subheader("Analysis Results")

            # Show loader while processing the analysis
            with st.spinner("Analyzing resume and generating feedback..."):
                response = analyze_text(resume_text, job_description)
            if response:
                try:
                    analysis = process_feedback(response)  # Parse response into JSON
                    
                    st.metric("Job Description Match", analysis.get("JD_Match", "N/A"))

                    with st.expander("🔑 Missing Keywords", expanded=True):
                        missing_keywords = analysis.get("MissingKeywords", [])
                        if missing_keywords:
                            st.write(", ".join(missing_keywords))
                        else:
                            st.write("No missing keywords identified.")

                    with st.expander("📝 Profile Summary", expanded=True):
                        st.markdown(analysis.get("Profile_Summary", "No summary provided."))

                    with st.expander("🔧 Enhancements to be Done", expanded=True):
                        enhancements = analysis.get("Enhancements_to_be_done", [])
                        if enhancements:
                            st.write(", ".join(enhancements))
                        else:
                            st.write("No missing keywords identified.")
                        
                except json.JSONDecodeError:
                    st.error("Error parsing the analysis response. Please try again.")
            else:
                st.error("Failed to generate analysis. Please check your API configuration or input data.")
        else:
            st.error("Failed to extract text from the uploaded file. Please ensure it's a valid PDF, DOCX, or TXT file.")

        # Cleanup temporary file
        os.remove(temp_file.name)
    elif uploaded_file and not job_description:
        st.warning("Please provide a job description for the analysis.")
    elif job_description and not uploaded_file:
        st.warning("Please upload a resume for the analysis.")

if __name__ == "__main__":
    main()