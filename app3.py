# app.py - Streamlit CV Generator App
import streamlit as st
import google.generativeai as genai
import markdown
from weasyprint import HTML
import io
import re
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AI CV Generator",
    page_icon="📝",
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
    .section-header {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #3498db;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #3498db;
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
    .form-section {
        background-color: #fafafa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'generated_cv' not in st.session_state:
    st.session_state.generated_cv = ""
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

def collect_user_information():
    """Collect comprehensive user information for CV generation"""
    user_data = {}
    
    st.markdown('<div class="section-header"><h3>👤 Personal Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        user_data['first_name'] = st.text_input("First Name *", placeholder="John")
        user_data['last_name'] = st.text_input("Last Name *", placeholder="Doe")
        user_data['email'] = st.text_input("Email Address *", placeholder="john.doe@email.com")
        user_data['phone'] = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
    
    with col2:
        user_data['location'] = st.text_input("Location", placeholder="City, State, Country")
        user_data['linkedin'] = st.text_input("LinkedIn Profile", placeholder="linkedin.com/in/johndoe")
        user_data['website'] = st.text_input("Personal Website/Portfolio", placeholder="www.johndoe.com")
    
    st.markdown('<div class="section-header"><h3>🎯 Professional Summary</h3></div>', unsafe_allow_html=True)
    user_data['summary'] = st.text_area(
        "Professional Summary (2-3 sentences about your career goals and key strengths)",
        placeholder="Motivated software developer with 3+ years experience...",
        height=100
    )
    
    st.markdown('<div class="section-header"><h3>🎓 Education</h3></div>', unsafe_allow_html=True)
    num_education = st.number_input("Number of Education Entries", min_value=1, max_value=5, value=1)
    
    education_entries = []
    for i in range(num_education):
        st.markdown(f"**Education Entry {i+1}:**")
        col1, col2 = st.columns(2)
        with col1:
            degree = st.text_input(f"Degree/Qualification", key=f"degree_{i}", placeholder="Bachelor of Science in Computer Science")
            institution = st.text_input(f"Institution", key=f"institution_{i}", placeholder="University of Technology")
        with col2:
            graduation_date = st.text_input(f"Graduation Date", key=f"grad_date_{i}", placeholder="May 2023")
            gpa = st.text_input(f"GPA (optional)", key=f"gpa_{i}", placeholder="3.8/4.0")
        
        if degree and institution:
            education_entries.append({
                'degree': degree,
                'institution': institution,
                'graduation_date': graduation_date,
                'gpa': gpa
            })
    
    user_data['education'] = education_entries
    
    st.markdown('<div class="section-header"><h3>💼 Work Experience</h3></div>', unsafe_allow_html=True)
    num_experience = st.number_input("Number of Work Experience Entries", min_value=0, max_value=10, value=2)
    
    experience_entries = []
    for i in range(num_experience):
        st.markdown(f"**Work Experience {i+1}:**")
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input(f"Job Title", key=f"job_title_{i}", placeholder="Software Developer")
            company = st.text_input(f"Company", key=f"company_{i}", placeholder="Tech Solutions Inc.")
        with col2:
            start_date = st.text_input(f"Start Date", key=f"start_date_{i}", placeholder="June 2021")
            end_date = st.text_input(f"End Date", key=f"end_date_{i}", placeholder="Present")
        
        responsibilities = st.text_area(
            f"Key Responsibilities & Achievements (one per line)",
            key=f"responsibilities_{i}",
            placeholder="• Developed web applications using React and Node.js\n• Improved system performance by 30%\n• Led a team of 3 developers",
            height=100
        )
        
        if job_title and company:
            experience_entries.append({
                'job_title': job_title,
                'company': company,
                'start_date': start_date,
                'end_date': end_date,
                'responsibilities': responsibilities
            })
    
    user_data['experience'] = experience_entries
    
    st.markdown('<div class="section-header"><h3>🛠️ Skills</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        user_data['technical_skills'] = st.text_area(
            "Technical Skills (comma-separated)",
            placeholder="Python, JavaScript, React, SQL, AWS, Docker",
            height=80
        )
    with col2:
        user_data['soft_skills'] = st.text_area(
            "Soft Skills (comma-separated)",
            placeholder="Leadership, Communication, Problem-solving, Teamwork",
            height=80
        )
    
    st.markdown('<div class="section-header"><h3>🏆 Additional Information</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        user_data['certifications'] = st.text_area(
            "Certifications (one per line)",
            placeholder="• AWS Certified Solutions Architect\n• Google Cloud Professional",
            height=80
        )
        user_data['languages'] = st.text_area(
            "Languages",
            placeholder="English (Native), Spanish (Fluent), French (Basic)",
            height=60
        )
    with col2:
        user_data['projects'] = st.text_area(
            "Notable Projects (optional)",
            placeholder="• E-commerce Platform - Built using MERN stack\n• Machine Learning Model - Predicted customer churn",
            height=80
        )
        user_data['awards'] = st.text_area(
            "Awards/Achievements (optional)",
            placeholder="• Employee of the Month - June 2023\n• Dean's List - Fall 2022",
            height=60
        )
    
    return user_data

def generate_cv_with_gemini(user_data, job_description, api_key):
    """Use Gemini API to generate a tailored CV"""
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert user data to structured format for the prompt
        newline = '\n'
        
        # Build full name
        full_name = f"{user_data.get('first_name', '').strip()} {user_data.get('last_name', '').strip()}".strip()
        
        # Helper function to build sections only if data exists
        def build_section(title, items):
            if not items:
                return ""
            return f"{title}:{newline}{items}{newline}"
        
        # Build personal info section (only include non-empty fields)
        personal_info = []
        personal_info.append(f"- Name: {full_name}" if full_name else "")
        personal_info.append(f"- Email: {user_data.get('email', '')}" if user_data.get('email', '').strip() else "")
        personal_info.append(f"- Phone: {user_data.get('phone', '')}" if user_data.get('phone', '').strip() else "")
        personal_info.append(f"- Location: {user_data.get('location', '')}" if user_data.get('location', '').strip() else "")
        personal_info.append(f"- LinkedIn: {user_data.get('linkedin', '')}" if user_data.get('linkedin', '').strip() else "")
        personal_info.append(f"- Website: {user_data.get('website', '')}" if user_data.get('website', '').strip() else "")
        
        # Filter out empty entries
        personal_info = [info for info in personal_info if info]
        personal_info_text = newline.join(personal_info) if personal_info else ""
        
        # Format education entries (only include if data exists)
        education_entries = []
        for edu in user_data.get('education', []):
            if edu.get('degree', '').strip() and edu.get('institution', '').strip():
                entry = f"• {edu.get('degree', '')} - {edu.get('institution', '')}"
                if edu.get('graduation_date', '').strip():
                    entry += f" ({edu.get('graduation_date', '')})"
                if edu.get('gpa', '').strip():
                    entry += f" - GPA: {edu.get('gpa', '')}"
                education_entries.append(entry)
        
        education_text = newline.join(education_entries) if education_entries else ""
        
        # Format experience entries (only include if data exists)
        experience_entries = []
        for exp in user_data.get('experience', []):
            if exp.get('job_title', '').strip() and exp.get('company', '').strip():
                entry = f"• {exp.get('job_title', '')} at {exp.get('company', '')}"
                
                # Add dates if provided
                start_date = exp.get('start_date', '').strip()
                end_date = exp.get('end_date', '').strip()
                if start_date and end_date:
                    entry += f" ({start_date} - {end_date})"
                elif start_date:
                    entry += f" ({start_date} - Present)"
                
                # Add responsibilities if provided
                if exp.get('responsibilities', '').strip():
                    entry += f"{newline}Responsibilities:{newline}{exp.get('responsibilities', '')}"
                
                experience_entries.append(entry)
        
        experience_text = newline.join(experience_entries) if experience_entries else ""
        
        # Build skills section (only if skills exist)
        skills_entries = []
        if user_data.get('technical_skills', '').strip():
            skills_entries.append(f"Technical: {user_data.get('technical_skills', '')}")
        if user_data.get('soft_skills', '').strip():
            skills_entries.append(f"Soft Skills: {user_data.get('soft_skills', '')}")
        
        skills_text = newline.join(skills_entries) if skills_entries else ""
        
        # Build additional info section (only include non-empty fields)
        additional_info = []
        if user_data.get('certifications', '').strip():
            additional_info.append(f"Certifications: {user_data.get('certifications', '')}")
        if user_data.get('languages', '').strip():
            additional_info.append(f"Languages: {user_data.get('languages', '')}")
        if user_data.get('projects', '').strip():
            additional_info.append(f"Projects: {user_data.get('projects', '')}")
        if user_data.get('awards', '').strip():
            additional_info.append(f"Awards: {user_data.get('awards', '')}")
        
        additional_info_text = newline.join(additional_info) if additional_info else ""
        
        # Build the complete user info text with only non-empty sections
        user_info_sections = []
        
        if personal_info_text:
            user_info_sections.append(f"PERSONAL INFORMATION:{newline}{personal_info_text}")
        
        if user_data.get('summary', '').strip():
            user_info_sections.append(f"PROFESSIONAL SUMMARY:{newline}{user_data.get('summary', '')}")
        
        if education_text:
            user_info_sections.append(f"EDUCATION:{newline}{education_text}")
        
        if experience_text:
            user_info_sections.append(f"WORK EXPERIENCE:{newline}{experience_text}")
        
        if skills_text:
            user_info_sections.append(f"SKILLS:{newline}{skills_text}")
        
        if additional_info_text:
            user_info_sections.append(f"ADDITIONAL INFORMATION:{newline}{additional_info_text}")
        
        user_info_text = f"{newline}{newline}".join(user_info_sections)

        prompt = f"""
You are a professional CV writer. Create a comprehensive, ATS-optimized CV based on the user information and tailored to the job description.

IMPORTANT: Output ONLY the complete CV in clean markdown format. Do not include any suggestions, advice, or additional text.

Guidelines:
- Use professional formatting with clear sections
- Tailor the content to match the job description keywords
- Prioritize relevant experience and skills
- Use strong action verbs and quantifiable achievements
- Ensure ATS optimization
- Keep it concise yet comprehensive
- Use bullet points for easy reading
- Include all provided information in a logical, professional manner

USER INFORMATION:
{user_info_text}

JOB DESCRIPTION TO TAILOR FOR:
{job_description}

OUTPUT THE COMPLETE CV IN MARKDOWN FORMAT:
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

def markdown_to_pdf(markdown_content):
    """Convert markdown content to PDF with professional styling"""
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Professional CV styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4;
                    margin: 1in;
                }}
                body {{
                    font-family: 'Calibri', 'Arial', sans-serif;
                    line-height: 1.5;
                    color: #333333;
                    max-width: 100%;
                    font-size: 11pt;
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 24pt;
                    margin-bottom: 5px;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 5px;
                }}
                h2 {{
                    color: #34495e;
                    font-size: 14pt;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    font-weight: bold;
                }}
                h3 {{
                    color: #2c3e50;
                    font-size: 12pt;
                    margin-bottom: 5px;
                    font-weight: bold;
                }}
                h4 {{
                    color: #7f8c8d;
                    font-size: 10pt;
                    margin-bottom: 5px;
                    font-style: italic;
                }}
                ul {{
                    margin-left: 20px;
                    margin-bottom: 10px;
                }}
                li {{
                    margin-bottom: 3px;
                }}
                p {{
                    margin-bottom: 8px;
                    text-align: justify;
                }}
                strong {{
                    color: #2c3e50;
                }}
                .contact-info {{
                    text-align: center;
                    margin-bottom: 20px;
                    color: #7f8c8d;
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

def main():
    # Header
    st.markdown('<h1 class="main-header">📝 AI CV Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 18px;">Create a professional CV tailored to any job description using AI</p>', unsafe_allow_html=True)
    
    # Sidebar for API key and instructions
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
        
        st.header("📋 How It Works")
        st.markdown("""
        1. **Enter your Gemini API key**
        2. **Provide the target job description**
        3. **Fill in your personal information**
        4. **Click 'Generate CV'**
        5. **Download your professional CV as PDF**
        """)
        
        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.markdown("- Be specific about your achievements")
        st.markdown("- Include quantifiable results when possible")
        st.markdown("- List relevant skills for the target job")
        st.markdown("- Keep descriptions concise but impactful")
    
    # Main content
    if not api_key:
        st.markdown('<div class="info-box">👈 Please enter your Gemini API key in the sidebar to get started.</div>', unsafe_allow_html=True)
        return
    
    # Job Description Section
    st.markdown('<div class="section-header"><h3>🎯 Target Job Description</h3></div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste the job description you want to tailor your CV for:",
        height=200,
        placeholder="""Example:
We are looking for a Software Developer with experience in Python, JavaScript, and cloud technologies. 
Responsibilities include developing web applications, working with databases, and collaborating with cross-functional teams.
Requirements: Bachelor's degree in Computer Science, 2+ years of experience, strong problem-solving skills."""
    )
    
    if not job_description:
        st.info("👆 Please provide the job description to continue.")
        return
    
    # User Information Collection
    st.markdown("---")
    st.markdown('<div class="section-header"><h3>📝 Your Information</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Fill in your details below. Fields marked with * are required. Empty fields will not appear in your final CV.</div>', unsafe_allow_html=True)
    
    user_data = collect_user_information()
    
    # Validation
    required_fields = ['first_name', 'last_name', 'email']
    missing_fields = [field.replace('_', ' ').title() for field in required_fields if not user_data.get(field, '').strip()]
    
    if missing_fields:
        st.error(f"Please fill in the required fields: {', '.join(missing_fields)}")
        return
    
    # Generate CV Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Professional CV", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is creating your professional CV... This may take a few moments."):
                generated_cv = generate_cv_with_gemini(user_data, job_description, api_key)
            
            if generated_cv:
                st.session_state.generated_cv = generated_cv
                st.session_state.user_data = user_data
                st.markdown('<div class="success-message">✅ CV generated successfully!</div>', unsafe_allow_html=True)
    
    # Display Generated CV
    if st.session_state.generated_cv:
        st.markdown("---")
        st.subheader("✨ Your Professional CV")
        
        # Display in columns
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(st.session_state.generated_cv)
        
        with col2:
            st.subheader("📥 Download Options")
            
            # Generate PDF
            pdf_bytes = markdown_to_pdf(st.session_state.generated_cv)
            
            if pdf_bytes:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                full_name = f"{st.session_state.user_data.get('first_name', '').strip()} {st.session_state.user_data.get('last_name', '').strip()}".strip()
                filename = f"{full_name.replace(' ', '_')}_CV_{timestamp}.pdf" if full_name else f"CV_{timestamp}.pdf"
                
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
                st.success("✅ PDF ready for download!")
            
            # Download as Markdown
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_name = f"{st.session_state.user_data.get('first_name', '').strip()} {st.session_state.user_data.get('last_name', '').strip()}".strip()
            md_filename = f"{full_name.replace(' ', '_')}_CV_{timestamp}.md" if full_name else f"CV_{timestamp}.md"
            
            st.download_button(
                label="📝 Download as Markdown",
                data=st.session_state.generated_cv,
                file_name=md_filename,
                mime="text/markdown",
                use_container_width=True
            )
            
            # Edit and Regenerate
            if st.button("✏️ Edit & Regenerate", use_container_width=True):
                st.session_state.generated_cv = ""
                st.experimental_rerun()
            
            # Clear All
            if st.button("🗑️ Start Over", use_container_width=True):
                st.session_state.generated_cv = ""
                st.session_state.user_data = {}
                st.experimental_rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #7f8c8d;">Made by JA ❤️ | Create professional CVs in minutes</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()