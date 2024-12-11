# **ATS_ResumeRefiner**

ATS_ResumeRefiner is a powerful AI-driven tool designed to analyze resumes and evaluate their alignment with specific job descriptions. Using advanced techniques like Zero-Shot, One-Shot, and Few-Shot learning, this application provides insightful feedback and a percentage match, making it easier for recruiters and job seekers to refine resumes for better results.

---

## **Features**
- **Zero-Shot Analysis**: Evaluate resumes without prior examples.
- **One-Shot Analysis**: Analyze resumes based on a single structured example.
- **Few-Shot Analysis**: Provide nuanced feedback by generalizing from multiple examples.
- **Match Percentage**: Quantify how well a resume aligns with the given job description.
- **Interactive Interface**: User-friendly interface built with Streamlit for seamless interaction.

---

## **Technologies Used**
- **Python**: Core programming language.
- **Streamlit**: For building an interactive web application.
- **Google Generative AI (Gemini)**: For AI-driven content generation.
- **PyPDF2**: For extracting text from uploaded PDFs.
- **pdf2image**: For converting PDF files to images.
- **Pillow (PIL)**: For image manipulation.
- **dotenv**: For managing API keys securely using environment variables.

---

## **Setup and Installation**
Follow these steps to set up and run the project on your local machine:

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/ATS_ResumeRefiner.git
cd ATS_ResumeRefiner
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
Copy code
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a .env file in the project root directory and add your Google Generative AI API key:

plaintext
Copy code
GOOGLE_API_KEY=your_api_key_here

### 5. Run the Application
```bash
Copy code
streamlit run app.py
```
## Screenshots

Here’s a screenshot of the application interface:

![Application Interface](images/ATS_ResumeRefiner.png)


---

## Future Enhancements

- Integrate more advanced AI models for improved analysis.
- Add support for additional file formats (e.g., DOCX).
- Implement a "Resume Builder" feature for automatic refinement.

---

## Contributing

If you'd like to contribute to this project:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request.

---

## Contact

For questions or feedback, feel free to reach out:

**Author:** Kusuma Reddyvari  
**Email:** kusumareddy28@gmail.com  
**GitHub:** [KusumaReddyvari](https://github.com/KusumaReddyvari)
