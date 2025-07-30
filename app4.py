# app.py - Streamlit LinkedIn Profile Optimizer App
import streamlit as st
import google.generativeai as genai
import markdown
from weasyprint import HTML
import io
import re
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AI LinkedIn Profile Optimizer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #0077b5;
        margin-bottom: 2rem;
    }
    .section-header {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #0077b5;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #0077b5;
    }
    .linkedin-preview {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    .linkedin-section {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background-color: #fafafa;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'optimized_profile' not in st.session_state:
    st.session_state.optimized_profile = ""
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

def collect_linkedin_information():
    """Collect comprehensive LinkedIn profile information"""
    user_data = {}
    
    st.markdown('<div class="section-header"><h3>👤 Basic Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        user_data['first_name'] = st.text_input("First Name *", placeholder="John")
        user_data['last_name'] = st.text_input("Last Name *", placeholder="Doe")
        user_data['current_title'] = st.text_input("Current Job Title *", placeholder="Software Engineer")
    
    with col2:
        user_data['location'] = st.text_input("Location", placeholder="San Francisco, CA")
        user_data['industry'] = st.text_input("Industry", placeholder="Technology")
        user_data['email'] = st.text_input("Email (for contact info)", placeholder="john.doe@email.com")
    
    st.markdown('<div class="section-header"><h3>🎯 Professional Headline</h3></div>', unsafe_allow_html=True)
    user_data['current_headline'] = st.text_area(
        "Current LinkedIn Headline (if you have one)",
        placeholder="Software Engineer at Tech Company | Python Developer | AI Enthusiast",
        height=60
    )
    
    st.markdown('<div class="section-header"><h3>📝 About Section</h3></div>', unsafe_allow_html=True)
    user_data['current_about'] = st.text_area(
        "Current About/Summary Section (if you have one)",
        placeholder="Passionate software engineer with 3+ years of experience in developing scalable web applications...",
        height=150
    )
    
    st.markdown('<div class="section-header"><h3>💼 Work Experience</h3></div>', unsafe_allow_html=True)
    num_experience = st.number_input("Number of Work Experience Entries", min_value=0, max_value=10, value=2)
    
    experience_entries = []
    for i in range(num_experience):
        st.markdown(f"**Experience {i+1}:**")
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input(f"Job Title", key=f"job_title_{i}", placeholder="Software Engineer")
            company = st.text_input(f"Company", key=f"company_{i}", placeholder="Tech Solutions Inc.")
            employment_type = st.selectbox(f"Employment Type", 
                ["Full-time", "Part-time", "Contract", "Freelance", "Internship"], 
                key=f"emp_type_{i}")
        with col2:
            start_date = st.text_input(f"Start Date", key=f"start_date_{i}", placeholder="Jan 2022")
            end_date = st.text_input(f"End Date", key=f"end_date_{i}", placeholder="Present")
            location = st.text_input(f"Location", key=f"job_location_{i}", placeholder="San Francisco, CA")
        
        description = st.text_area(
            f"Job Description/Achievements",
            key=f"job_description_{i}",
            placeholder="• Developed and maintained web applications using React and Node.js\n• Improved system performance by 30% through code optimization\n• Led a cross-functional team of 5 developers",
            height=100
        )
        
        if job_title and company:
            experience_entries.append({
                'job_title': job_title,
                'company': company,
                'employment_type': employment_type,
                'start_date': start_date,
                'end_date': end_date,
                'location': location,
                'description': description
            })
    
    user_data['experience'] = experience_entries
    
    st.markdown('<div class="section-header"><h3>🎓 Education</h3></div>', unsafe_allow_html=True)
    num_education = st.number_input("Number of Education Entries", min_value=0, max_value=5, value=1)
    
    education_entries = []
    for i in range(num_education):
        st.markdown(f"**Education {i+1}:**")
        col1, col2 = st.columns(2)
        with col1:
            degree = st.text_input(f"Degree", key=f"degree_{i}", placeholder="Bachelor of Science in Computer Science")
            school = st.text_input(f"School", key=f"school_{i}", placeholder="University of Technology")
        with col2:
            start_year = st.text_input(f"Start Year", key=f"edu_start_{i}", placeholder="2018")
            end_year = st.text_input(f"End Year", key=f"edu_end_{i}", placeholder="2022")
        
        activities = st.text_area(
            f"Activities/Achievements (optional)",
            key=f"activities_{i}",
            placeholder="Dean's List, Computer Science Club President, Hackathon Winner",
            height=60
        )
        
        if degree and school:
            education_entries.append({
                'degree': degree,
                'school': school,
                'start_year': start_year,
                'end_year': end_year,
                'activities': activities
            })
    
    user_data['education'] = education_entries
    
    st.markdown('<div class="section-header"><h3>🛠️ Skills & Endorsements</h3></div>', unsafe_allow_html=True)
    user_data['skills'] = st.text_area(
        "Skills (comma-separated, list your top 10-15 skills)",
        placeholder="Python, JavaScript, React, Node.js, AWS, Docker, Machine Learning, SQL, Git, Agile Development",
        height=80
    )
    
    st.markdown('<div class="section-header"><h3>🏆 Additional Sections</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        user_data['certifications'] = st.text_area(
            "Certifications",
            placeholder="AWS Certified Solutions Architect\nGoogle Cloud Professional Developer\nScrum Master Certification",
            height=80
        )
        user_data['languages'] = st.text_area(
            "Languages",
            placeholder="English (Native)\nSpanish (Professional)\nFrench (Conversational)",
            height=60
        )
    with col2:
        user_data['projects'] = st.text_area(
            "Notable Projects",
            placeholder="E-commerce Platform - Full-stack web application\nAI Chatbot - Natural language processing project\nMobile App - React Native application",
            height=80
        )
        user_data['volunteer'] = st.text_area(
            "Volunteer Experience",
            placeholder="Code Mentor at Local Coding Bootcamp\nTech Volunteer at Non-profit Organization",
            height=60
        )
    
    return user_data

def optimize_linkedin_with_gemini(user_data, target_role, api_key):
    """Use Gemini API to optimize LinkedIn profile"""
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert user data to structured format
        newline = '\n'
        
        # Build full name
        full_name = f"{user_data.get('first_name', '').strip()} {user_data.get('last_name', '').strip()}".strip()
        
        # Format experience entries
        experience_entries = []
        for exp in user_data.get('experience', []):
            if exp.get('job_title', '').strip() and exp.get('company', '').strip():
                entry = f"• {exp.get('job_title', '')} at {exp.get('company', '')}"
                entry += f" ({exp.get('employment_type', 'Full-time')})"
                
                # Add dates if provided
                if exp.get('start_date', '').strip() and exp.get('end_date', '').strip():
                    entry += f" | {exp.get('start_date', '')} - {exp.get('end_date', '')}"
                
                # Add location if provided
                if exp.get('location', '').strip():
                    entry += f" | {exp.get('location', '')}"
                
                # Add description if provided
                if exp.get('description', '').strip():
                    entry += f"{newline}{exp.get('description', '')}"
                
                experience_entries.append(entry)
        
        experience_text = newline.join(experience_entries) if experience_entries else ""
        
        # Format education entries
        education_entries = []
        for edu in user_data.get('education', []):
            if edu.get('degree', '').strip() and edu.get('school', '').strip():
                entry = f"• {edu.get('degree', '')} - {edu.get('school', '')}"
                
                if edu.get('start_year', '').strip() and edu.get('end_year', '').strip():
                    entry += f" ({edu.get('start_year', '')} - {edu.get('end_year', '')})"
                
                if edu.get('activities', '').strip():
                    entry += f"{newline}Activities: {edu.get('activities', '')}"
                
                education_entries.append(entry)
        
        education_text = newline.join(education_entries) if education_entries else ""
        
        # Build user info sections
        user_info_sections = []
        
        # Basic info
        basic_info = [f"Name: {full_name}"]
        if user_data.get('current_title', '').strip():
            basic_info.append(f"Current Title: {user_data.get('current_title', '')}")
        if user_data.get('location', '').strip():
            basic_info.append(f"Location: {user_data.get('location', '')}")
        if user_data.get('industry', '').strip():
            basic_info.append(f"Industry: {user_data.get('industry', '')}")
        
        user_info_sections.append(f"BASIC INFORMATION:{newline}{newline.join(basic_info)}")
        
        # Current profile content
        if user_data.get('current_headline', '').strip():
            user_info_sections.append(f"CURRENT HEADLINE:{newline}{user_data.get('current_headline', '')}")
        
        if user_data.get('current_about', '').strip():
            user_info_sections.append(f"CURRENT ABOUT SECTION:{newline}{user_data.get('current_about', '')}")
        
        # Experience
        if experience_text:
            user_info_sections.append(f"WORK EXPERIENCE:{newline}{experience_text}")
        
        # Education
        if education_text:
            user_info_sections.append(f"EDUCATION:{newline}{education_text}")
        
        # Skills
        if user_data.get('skills', '').strip():
            user_info_sections.append(f"SKILLS:{newline}{user_data.get('skills', '')}")
        
        # Additional sections
        additional_info = []
        if user_data.get('certifications', '').strip():
            additional_info.append(f"Certifications:{newline}{user_data.get('certifications', '')}")
        if user_data.get('projects', '').strip():
            additional_info.append(f"Projects:{newline}{user_data.get('projects', '')}")
        if user_data.get('volunteer', '').strip():
            additional_info.append(f"Volunteer Experience:{newline}{user_data.get('volunteer', '')}")
        if user_data.get('languages', '').strip():
            additional_info.append(f"Languages:{newline}{user_data.get('languages', '')}")
        
        if additional_info:
            user_info_sections.append(f"ADDITIONAL INFORMATION:{newline}{newline.join(additional_info)}")
        
        user_info_text = f"{newline}{newline}".join(user_info_sections)

        prompt = f"""
You are a LinkedIn profile optimization expert. Create an optimized LinkedIn profile that will attract recruiters and align with the target role.

IMPORTANT: Structure your response with clear sections for each part of the LinkedIn profile. Use professional language that's engaging and keyword-rich.

Guidelines:
- Create a compelling professional headline (120 characters max)
- Write an engaging About/Summary section (2000 characters max)
- Optimize job descriptions with strong action verbs and quantified achievements
- Suggest skill prioritization for the target role
- Use industry keywords naturally
- Make it ATS-friendly and recruiter-appealing
- Maintain authenticity while optimizing for discoverability

USER PROFILE INFORMATION:
{user_info_text}

TARGET ROLE/CAREER GOAL:
{target_role}

OUTPUT FORMAT:
Structure your response as follows:

# OPTIMIZED LINKEDIN PROFILE

## Professional Headline
[Optimized headline here]

## About Section
[Optimized about/summary section here]

## Experience Section Improvements
[Provide optimized descriptions for each job, maintaining chronological order]

## Skills Optimization
[Prioritized list of skills for the target role]

## Additional Recommendations
[Any other suggestions for profile improvement]

Create the optimized profile now:
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
    """Convert markdown content to PDF with LinkedIn-style formatting"""
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # LinkedIn-style formatting
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
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    max-width: 100%;
                    font-size: 11pt;
                }}
                h1 {{
                    color: #0077b5;
                    font-size: 24pt;
                    margin-bottom: 10px;
                    text-align: center;
                    border-bottom: 2px solid #0077b5;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #0077b5;
                    font-size: 16pt;
                    margin-top: 25px;
                    margin-bottom: 10px;
                    font-weight: bold;
                }}
                h3 {{
                    color: #2c3e50;
                    font-size: 14pt;
                    margin-bottom: 8px;
                }}
                ul {{
                    margin-left: 20px;
                    margin-bottom: 15px;
                }}
                li {{
                    margin-bottom: 5px;
                }}
                p {{
                    margin-bottom: 10px;
                    text-align: justify;
                }}
                strong {{
                    color: #0077b5;
                }}
                .linkedin-section {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #0077b5;
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
    st.markdown('<h1 class="main-header">💼 AI LinkedIn Profile Optimizer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 18px;">Optimize your LinkedIn profile to attract recruiters and land your dream job</p>', unsafe_allow_html=True)
    
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
        2. **Specify your target role/career goal**
        3. **Fill in your current LinkedIn information**
        4. **Click 'Optimize Profile'**
        5. **Get your optimized LinkedIn content**
        6. **Copy and paste to your LinkedIn profile**
        """)
        
        st.markdown("---")
        st.markdown("**💡 LinkedIn Tips:**")
        st.markdown("- Use a professional headshot")
        st.markdown("- Keep your headline under 120 characters")
        st.markdown("- Write in first person for About section")
        st.markdown("- Use industry keywords naturally")
        st.markdown("- Update regularly with new achievements")
    
    # Main content
    if not api_key:
        st.markdown('<div class="info-box">👈 Please enter your Gemini API key in the sidebar to get started.</div>', unsafe_allow_html=True)
        return
    
    # Target Role Section
    st.markdown('<div class="section-header"><h3>🎯 Target Role & Career Goal</h3></div>', unsafe_allow_html=True)
    target_role = st.text_area(
        "What role or career direction are you targeting? (Be specific)",
        height=100,
        placeholder="""Example:
Senior Software Engineer specializing in full-stack development with React and Node.js. 
Looking to work at a fast-growing tech startup in the fintech space. 
Interested in leadership opportunities and mentoring junior developers."""
    )
    
    if not target_role:
        st.info("👆 Please describe your target role to continue.")
        return
    
    # User Information Collection
    st.markdown("---")
    st.markdown('<div class="section-header"><h3>📝 Current LinkedIn Information</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Fill in your current LinkedIn information. Fields marked with * are required. You can fill in as much or as little as you have - the AI will work with what you provide.</div>', unsafe_allow_html=True)
    
    user_data = collect_linkedin_information()
    
    # Validation
    required_fields = ['first_name', 'last_name', 'current_title']
    missing_fields = [field.replace('_', ' ').title() for field in required_fields if not user_data.get(field, '').strip()]
    
    if missing_fields:
        st.error(f"Please fill in the required fields: {', '.join(missing_fields)}")
        return
    
    # Optimize Profile Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Optimize LinkedIn Profile", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is optimizing your LinkedIn profile... This may take a few moments."):
                optimized_profile = optimize_linkedin_with_gemini(user_data, target_role, api_key)
            
            if optimized_profile:
                st.session_state.optimized_profile = optimized_profile
                st.session_state.user_data = user_data
                st.markdown('<div class="success-message">✅ LinkedIn profile optimized successfully!</div>', unsafe_allow_html=True)
    
    # Display Optimized Profile
    if st.session_state.optimized_profile:
        st.markdown("---")
        st.subheader("✨ Your Optimized LinkedIn Profile")
        
        # Display in columns
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown('<div class="linkedin-preview">', unsafe_allow_html=True)
            st.markdown(st.session_state.optimized_profile)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("📥 Download & Share")
            
            # Generate PDF
            pdf_bytes = markdown_to_pdf(st.session_state.optimized_profile)
            
            if pdf_bytes:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                full_name = f"{st.session_state.user_data.get('first_name', '').strip()} {st.session_state.user_data.get('last_name', '').strip()}".strip()
                filename = f"{full_name.replace(' ', '_')}_LinkedIn_Profile_{timestamp}.pdf" if full_name else f"LinkedIn_Profile_{timestamp}.pdf"
                
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
            md_filename = f"{full_name.replace(' ', '_')}_LinkedIn_Profile_{timestamp}.md" if full_name else f"LinkedIn_Profile_{timestamp}.md"
            
            st.download_button(
                label="📝 Download as Text",
                data=st.session_state.optimized_profile,
                file_name=md_filename,
                mime="text/markdown",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("**📋 How to Use:**")
            st.markdown("1. Copy each section")
            st.markdown("2. Paste into your LinkedIn profile")
            st.markdown("3. Customize as needed")
            st.markdown("4. Save and publish!")
            
            # Edit and Regenerate
            if st.button("✏️ Edit & Regenerate", use_container_width=True):
                st.session_state.optimized_profile = ""
                st.experimental_rerun()
            
            # Clear All
            if st.button("🗑️ Start Over", use_container_width=True):
                st.session_state.optimized_profile = ""
                st.session_state.user_data = {}
                st.experimental_rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #7f8c8d;">Made by JA ❤️ | Optimize your LinkedIn presence in minutes</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()