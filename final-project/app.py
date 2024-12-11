from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
import io
import base64
import re

# Configure the Generative AI client with the API key stored in environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    """
    Generate AI-based content using the gemini model.

    Parameters:
    - input_text: The textual job description or prompt input.
    - pdf_content: A list containing one or more PDF page content entries (in this case, an image).
    - prompt: A string containing instructions or context for the AI model.

    Returns:
    - The AI-generated response as a string.
    """

    # Create an instance of the gemini model (version 'gemini-1.5-flash')
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Generate content by providing the input text, the first element of pdf_content,
    # and the prompt. The model uses these three elements to produce a response.
    response = model.generate_content([input_text, pdf_content[0], prompt])

    # Return only the text portion of the response for further use
    return response.text

def input_pdf_setup(uploaded_file):
    """
    Convert the first page of the uploaded PDF into a base64 encoded JPEG image
    that can be passed as content to the Generative AI model.

    Parameters:
    - uploaded_file: The uploaded PDF file from the user interface.

    Returns:
    - A list (pdf_parts) containing a dictionary with mime_type and data keys:
      - mime_type: the type of the file (image/jpeg)
      - data: the base64-encoded string of the first PDF page image
    """

    # Check if a file is uploaded
    if uploaded_file is not None:
        # Convert the PDF into a list of images (one image per page).
        # convert_from_bytes reads the PDF bytes and returns a list of PIL images.
        images = pdf2image.convert_from_bytes(uploaded_file.read())

        # Take the first page of the PDF as the primary content
        first_page = images[0]

        # Create a BytesIO object to hold the image data in memory
        img_byte_arr = io.BytesIO()

        # Save the first page image in JPEG format into the BytesIO stream
        first_page.save(img_byte_arr, format='JPEG')

        # Get the raw bytes of the image
        img_byte_arr = img_byte_arr.getvalue()

        # Encode the image bytes to a base64 string so it can be passed to the model
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                # base64.b64encode returns bytes, so decode it into a UTF-8 string
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]

        # Return the list containing the base64 encoded image data
        return pdf_parts
    else:
        # If no file is uploaded, raise a FileNotFoundError
        raise FileNotFoundError("No file uploaded")


# Prompts for different AI evaluation modes
# Make sure these prompts instruct the AI to provide a "Relevance Percentage: XX%" line
zero_shot_prompt = """
You are an AI tasked with evaluating the provided resume against the given job description.
Return a professional evaluation focusing on whether the candidate's profile aligns with the role, 
highlighting strengths and weaknesses. At the end of your response, include a line:
"Relevance Percentage: XX%"
"""

one_shot_prompt = """
Example:
Job Description: "Looking for a Full Stack Developer with React, Node.js, and Docker experience."
Resume: "3 years of experience in React, Node.js, and containerized applications with Docker."
Evaluation: 
- Candidate matches all required skills.
- Relevance Percentage: 100%

Now evaluate the following:
Job Description: {job_description}
Resume: {resume_content}

At the end of your response, always include:
"Relevance Percentage: XX%"
"""

few_shot_prompt = """
Example 1:
Job Description: "Data Scientist with Python, TensorFlow, and SQL."
Resume: "5 years in Python, TensorFlow, SQL, plus data analysis."
Evaluation:
- Excellent match for the requirements.
Relevance Percentage: 100%

Example 2:
Job Description: "Web Developer with HTML, CSS, JavaScript."
Resume: "Experience in HTML and CSS, but lacks JavaScript."
Evaluation:
- Partial match.
Relevance Percentage: 66.7%

Now evaluate the following:
Job Description: {job_description}
Resume: {resume_content}

At the end of your evaluation, include:
"Relevance Percentage: XX%"
"""

def get_prompt(job_desc, resume_text, mode):
    """
    Return the appropriate prompt based on the selected mode.

    Parameters:
    - job_desc: The job description text provided by the user.
    - resume_text: The extracted or representative text from the user's resume.
    - mode: A string indicating the learning mode ("Zero-Shot", "One-Shot", "Few-Shot").

    Returns:
    - A prompt string tailored to the chosen mode. For One-Shot and Few-Shot,
      placeholders in the prompt are replaced with the actual job description 
      and resume content.
    """

    # If Zero-Shot mode is selected, return the zero_shot_prompt without formatting
    if mode == "Zero-Shot":
        return zero_shot_prompt
    # If One-Shot mode is selected, format the one_shot_prompt with the provided job description and resume content
    elif mode == "One-Shot":
        return one_shot_prompt.format(job_description=job_desc, resume_content=resume_text)
    # If Few-Shot mode is selected, format the few_shot_prompt similarly
    elif mode == "Few-Shot":
        return few_shot_prompt.format(job_description=job_desc, resume_content=resume_text)


def extract_percentage(response):
    """
    Extract 'Relevance Percentage' or compute it from 'Total Score' in the AI response.

    Parameters:
    - response: The string response from the AI model.

    Process:
    1. Attempt to find a "Relevance Percentage:" line. If found, return the numeric percentage.
    2. If not found, attempt to find a "Total Score: X/Y" line and compute the percentage as (X/Y)*100.
    3. If neither is found, return None.

    Returns:
    - A float representing the relevance percentage, or None if no valid percentage could be extracted.
    """

    # Try to find a line matching "Relevance Percentage: XX%"
    match = re.search(r'Relevance Percentage:\s*([\d.]+)%', response, re.IGNORECASE)
    if match:
        # If found, convert the extracted value to a float and return it
        return float(match.group(1))
    else:
        # If no relevance percentage found, look for a "Total Score: X out of Y" format
        score_match = re.search(r'Total Score:\s*(\d+)\s*(?:\/|out of)\s*(\d+)', response, re.IGNORECASE)
        if score_match:
            # Extract the obtained score (X) and the max score (Y)
            obtained_score = float(score_match.group(1))
            max_score = float(score_match.group(2))
            # Compute a percentage and return it
            return round((obtained_score / max_score) * 100, 2)
    # If no percentage or total score is found, return None
    return None


# Configure the Streamlit application page
st.set_page_config(page_title='ATS Resume Expert', page_icon="📄", layout="wide")

# Sidebar UI elements for file upload, job description input, and learning mode selection
with st.sidebar:
    st.header("📄 Upload Resume")
    # Allow the user to upload a PDF resume file
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])

    st.header("📋 Job Description")
    # Text area for the user to input or paste the job description
    input_text = st.text_area("Paste Job Description:", key="input")

    st.header("⚙️ Learning Mode")
    # Radio buttons for selecting the learning mode (Zero-Shot, One-Shot, Few-Shot)
    learning_mode = st.radio("Select the mode:", ("Zero-Shot", "One-Shot", "Few-Shot"))

    # If a file has been uploaded, show a success message
    if uploaded_file:
        st.success("Resume uploaded successfully!")

# Main title and instructions on the page
st.title("📄 ATS Resume Expert")
st.markdown("""
Analyze your resume against a given job description using different AI evaluation modes:
- **Zero-Shot:** No prior examples given.
- **One-Shot:** One example given before evaluating.
- **Few-Shot:** Multiple examples given before evaluating.

**Choose an option in the sidebar and get started!**
""")

# Create two columns for placing the action buttons
col1, col2 = st.columns(2)
with col1:
    # Button to trigger a general evaluation ("Tell me about my resume")
    submit1 = st.button("Tell me about my resume")
with col2:
    # Button to trigger a percentage match analysis
    submit2 = st.button("Percentage Match")


if submit1 or submit2:
    if uploaded_file and input_text:
        # Extract resume content for prompt formatting
        pdf_content = input_pdf_setup(uploaded_file)
        
        # We can just say "Resume content embedded" since the actual text is in PDF form.
        # If needed, you could also extract actual text and include it in the prompt.
        # For simplicity, we're relying on the image content here. 
        # Ideally, you'd extract the text from the PDF and insert it into the prompt.
        
        # Extract text from PDF if needed:
        # Note: If you want actual text in prompt, uncomment below lines
        # from PyPDF2 import PdfReader
        # reader = PdfReader(uploaded_file)
        # resume_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        # For now, just put a placeholder since the AI is handling image content.
        resume_text = "Resume content embedded as an image."

        chosen_prompt = get_prompt(input_text, resume_text, learning_mode)
        response = get_gemini_response(input_text, pdf_content, chosen_prompt)

        # Display the raw AI response for verification
        st.write("### AI Response:")
        st.write(response)

        if submit2:
            # Extract and display the percentage match
            ai_percentage = extract_percentage(response)
            if ai_percentage is not None:
                st.markdown(f"### Match Percentage: **{ai_percentage}%**")
                st.progress(ai_percentage / 100)
            else:
                st.warning("No percentage could be extracted from the response. Please adjust the prompt or model output format.")
        else:
            # Just display the evaluation without extracting percentage
            st.subheader("The response is")
            st.write(response)

    else:
        st.warning("Please upload a PDF and provide a job description before proceeding.")
