# ResumeLLM

# Resume Analyzer with Enhanced ATS Feedback

This project is a **Resume Analyzer** that evaluates a resume against a provided job description and generates actionable feedback. It uses **spaCy** for natural language processing and **Google Gemini** (Generative AI) for detailed analysis and recommendations. The tool highlights the match percentage between the resume and job description, missing keywords, a profile summary, and enhancement suggestions for improving the resume.

## Features
- Upload resumes in PDF, DOCX, or TXT formats.
- Paste a job description for detailed analysis.
- Displays:
  - **JD Match**: A percentage match between the resume and job description.
  - **Missing Keywords**: Keywords that should be included in the resume.
  - **Profile Summary**: A brief summary of the resume.
  - **Enhancements to be done**: Suggestions for improving the resume.

## Technologies
- **spaCy**: Used for basic NLP processing.
- **Google Gemini**: Used to generate resume evaluation and actionable feedback.
- **Streamlit**: For building the interactive web interface.
- **PyPDF2**: For extracting text from PDF resumes.
- **python-docx**: For extracting text from DOCX resumes.
- **dotenv**: For managing environment variables (API keys).

## Installation

### Prerequisites
Make sure you have Python 3.x installed on your machine.

1. Clone the repository:
   ```bash
   git clone https://github.com/harshith-118/ResumeLLM.git
   cd ResumeLLM
2.	**Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**:
     - Create a .env file in the root directory.
     - Add the following:
   ```bash
   GOOGLE_API_KEY=your_google_api_key
   ```
4. **Run the application**:
   ```bash
   streamlit run app.py
   ```
