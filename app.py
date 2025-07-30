# app.py - Streamlit Resume Optimizer App
import streamlit as st
import google.generativeai as genai
import markdown
from weasyprint import HTML
import PyPDF2
import io
import re
import tempfile
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'optimized_resume' not in st.session_state:
    st.session_state.optimized_resume = ""

def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def optimize_resume_with_gemini(resume_text, job_description, api_key):
    """Use Gemini API to optimize the resume"""
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
You are a professional resume optimization expert. Your task is to rewrite the provided resume to perfectly match the job description requirements.

IMPORTANT: You must output ONLY the complete rewritten resume in markdown format. Do not include any suggestions, advice, or additional text after the resume.

Follow these guidelines while rewriting:
- Keep only the 2-3 most relevant work experiences 
- Use 2-3 bullet points per role focusing on achievements most relevant to the job
- Include quantifiable results (percentages, dollar amounts, etc.)
- Use strong action verbs
- Integrate keywords from the job description naturally
- Ensure ATS optimization
- Maintain professional formatting

---

RESUME TO OPTIMIZE:
{resume_text}

---

JOB DESCRIPTION:
{job_description}

---

OUTPUT ONLY THE REWRITTEN RESUME IN MARKDOWN FORMAT:
"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000,
                top_p=0.8,
                top_k=40
            )
        )
        
        return response.text
    
    except Exception as e:
        st.error(f"Error calling Gemini API: {str(e)}")
        return None

def clean_resume_content(resume_text):
    """Clean up the resume content and ensure proper formatting"""
    # Remove any remaining suggestions text
    end_patterns = [
        r'\n#+\s*Additional Suggestions.*',
        r'\n#+\s*Actionable Suggestions.*',
        r'\n#+\s*Recommendations.*',
        r'\n\*\*Additional Suggestions\*\*.*',
        r'\nThis optimized resume.*',
        r'\nActionable Suggestions:.*'
    ]
    
    for pattern in end_patterns:
        match = re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL)
        if match:
            resume_text = resume_text[:match.start()]
            break
    
    # Remove extra whitespace
    resume_text = re.sub(r'\n\n\n+', '\n\n', resume_text)
    
    return resume_text.strip()

def markdown_to_pdf(markdown_content):
    """Convert markdown content to PDF"""
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Add styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                    max-width: 800px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                    font-size: 28px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 25px;
                    font-size: 20px;
                }}
                h3 {{
                    color: #7f8c8d;
                    font-size: 16px;
                }}
                ul {{
                    margin-left: 20px;
                }}
                li {{
                    margin-bottom: 5px;
                }}
                p {{
                    margin-bottom: 10px;
                }}
                strong {{
                    color: #2c3e50;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        pdf_bytes = HTML(string=styled_html).write_pdf()
        return pdf_bytes
    
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 AI Resume Optimizer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 18px;">Transform your resume to match any job description using AI</p>', unsafe_allow_html=True)
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get your free API key from: https://makersuite.google.com/app/apikey"
        )
        st.session_state.api_key = api_key
        
        if not api_key:
            st.warning("Please enter your Gemini API key to continue.")
            st.info("Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        
        st.header("📋 Instructions")
        st.markdown("""
        1. **Enter your Gemini API key** (free from Google AI Studio)
        2. **Upload your current resume** as PDF
        3. **Paste the job description** you're targeting
        4. **Click 'Optimize Resume'** to get your tailored resume
        5. **Download the optimized PDF**
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("📄 Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume PDF file",
            type="pdf",
            help="Upload your current resume in PDF format"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            st.success(f"✅ Resume uploaded: {uploaded_file.name}")
            
            # Extract text from PDF
            with st.spinner("Extracting text from PDF..."):
                resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                with st.expander("📖 Preview Extracted Text"):
                    st.text_area("Resume Content", resume_text, height=200, disabled=True)
    
    with col2:
        st.subheader("🎯 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Paste the full job description, including requirements, responsibilities, and qualifications..."
        )
    
    # Optimization section
    if uploaded_file and job_description and api_key:
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Optimize Resume", type="primary", use_container_width=True):
                if resume_text:
                    with st.spinner("🤖 AI is optimizing your resume... This may take a few moments."):
                        optimized_resume = optimize_resume_with_gemini(resume_text, job_description, api_key)
                    
                    if optimized_resume:
                        # Clean the optimized resume
                        cleaned_resume = clean_resume_content(optimized_resume)
                        st.session_state.optimized_resume = cleaned_resume
                        
                        st.markdown('<div class="success-message">✅ Resume optimized successfully!</div>', unsafe_allow_html=True)
                else:
                    st.error("Could not extract text from the uploaded PDF. Please try a different file.")
    
    # Display optimized resume
    if st.session_state.optimized_resume:
        st.markdown("---")
        st.subheader("✨ Optimized Resume")
        
        # Display in two columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(st.session_state.optimized_resume)
        
        with col2:
            st.subheader("📥 Download")
            
            # Generate PDF
            pdf_bytes = markdown_to_pdf(st.session_state.optimized_resume)
            
            if pdf_bytes:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"optimized_resume_{timestamp}.pdf"
                
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
                st.success("✅ PDF ready for download!")
            
            # Download as markdown
            st.download_button(
                label="📝 Download Markdown",
                data=st.session_state.optimized_resume,
                file_name=f"optimized_resume_{timestamp}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
            # Clear button
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.optimized_resume = ""
                st.experimental_rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #7f8c8d;">Made by ❤️ JA</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()


#conda create -n gemini-env python=3.11
#conda activate gemini-env

# Then install the package
#pip install google-generativeai
#pip install streamlit
#pip install markdown
#pip install weasyprint
#pip install PyPDF2