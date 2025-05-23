import streamlit as st
import openai
import docx2txt
import fitz  # PyMuPDF
import re

# Initialize OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Function to extract text from DOCX
def extract_text_from_docx(uploaded_file):
    try:
        return docx2txt.process(uploaded_file)
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

# Function to score resume using OpenAI
def score_resume(cv_text):
    prompt = f"""
    You are an expert career coach and recruiter. Analyze the following resume based on global hiring standards.
    Score the resume out of 100, with a breakdown for these parameters (each out of the specified max points):
    1. Formatting (15): Clean layout, consistent fonts, clear headings.
    2. Grammar and Spelling (10): No errors or typos.
    3. Clarity and Impact (20): Clear, action-driven sentences with strong verbs.
    4. Role Relevance (20): Alignment with common job roles (e.g., manager, analyst).
    5. Keyword Optimization (15): Use of industry-specific terms.
    6. ATS Compatibility (10): Parsable layout, no complex tables/images.
    7. Length and Relevance (10): Ideal length for experience level.

    Provide:
    - Total score (/100)
    - Individual scores for each parameter
    - Specific suggestions for improvement for each parameter

    Resume:
    {cv_text}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error with OpenAI API: {e}")
        return "Analysis failed. Please check your API key or try again later."

# Main Streamlit app
def main():
    st.set_page_config(page_title="AI CV Scoring Tool", page_icon="📄")
    st.title("📄 AI CV Scoring Tool")
    st.markdown("Upload your resume (PDF or DOCX) to get a score based on global hiring standards and personalized improvement tips.")

    # File uploader
    uploaded_file = st.file_uploader("Choose your resume (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file:
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            cv_text = extract_text_from_pdf(uploaded_file)
        else:
            cv_text = extract_text_from_docx(uploaded_file)

        if cv_text:
            st.subheader("Extracted Resume Text")
            with st.expander("View Extracted Text"):
                st.write(cv_text)

            # Analyze resume
            if st.button("🔍 Analyze Resume"):
                with st.spinner("Analyzing your resume..."):
                    analysis = score_resume(cv_text)
                    st.success("✅ Analysis Complete!")
                    st.markdown("### Analysis Results")
                    st.write(analysis)

                    # Option to download analysis
                    st.download_button(
                        label="Download Analysis",
                        data=analysis,
                        file_name="resume_analysis.txt",
                        mime="text/plain"
                    )

    # Optional job description matching (placeholder for future expansion)
    st.markdown("---")
    st.subheader("Optional: Job Description Matching")
    st.write("Want to check how well your CV matches a specific job? (Coming soon!)")

if __name__ == "__main__":
    main()
