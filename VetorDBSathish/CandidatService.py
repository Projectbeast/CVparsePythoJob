from flask import Flask, request, jsonify

import os
import PyPDF2

import pandas as pd
from sentence_transformers import SentenceTransformer
from flask_cors import CORS
from utils.text_processing import preprocess_text
from utils.resume_parser import parse_resume
from sklearn.metrics.pairwise import cosine_similarity

from docx import Document  # Library for reading .docx files

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Create a directory to store uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        # Save the file temporarily
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

         # Extract text based on the file type
        if file.filename.endswith('.pdf'):
            extracted_text = pdf_to_text(file_path)
        elif file.filename.endswith('.docx'):
            extracted_text = docx_to_text(file_path)

        # Print extracted text to console
        processedText=process_resume(extracted_text)
        return jsonify({"message": "File uploaded successfully", "text": processedText}), 200
    else:
            return jsonify({"error": "File format not supported. Please upload a PDF or DOCX file."}), 400

def __init__(self, job_listings_path=None):
    self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    if job_listings_path:
        self.jobs_df = pd.read_csv(job_listings_path)
        self.jobs_df['processed_description'] = self.jobs_df['description'].apply(preprocess_text)
        self.job_embeddings = self.model.encode(self.jobs_df['processed_description'].tolist())

    # Initialize Gemini
    # genai.configure(api_key='AIzaSyAQyxQ3i3LhU_ocwWN7kHe7CwRjIRVsbBw')
    # self.gemini = genai.GenerativeModel('gemini-pro')


def pdf_to_text(file_path):
    text = ''
    try:
        # Open the PDF file
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        return f"Error processing PDF: {str(e)}"
    
    return text

def docx_to_text(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def process_resume(self,resume_text):
        processed_resume = preprocess_text(resume_text)
        resume_embedding = self.model.encode([processed_resume])[0]

        similarities = cosine_similarity([resume_embedding], self.job_embeddings)[0]
        top_indices = similarities.argsort()[-5:][::-1]

        recommendations = []
        for idx in top_indices:
            job_title = self.jobs_df.iloc[idx]['title']
            job_description = self.jobs_df.iloc[idx]['description']
            similarity = similarities[idx]

            # Use Gemini to generate a personalized job description
            prompt =f"""
                Given the following job description and a candidate's resume:
        
                Job Description:
                {job_description}
        
                Candidate's Resume:
                {resume_text}
        
                Please provide:
                1. A list of matching skills between the resume and the job description
                2. Any additional skills or qualifications the candidate might need for this role
                3. Suggestions for how the candidate can improve their resume for this specific job
                4. Any relevant certifications or training that could enhance the candidate's profile for this position
                """
            response = self.gemini.generate_content(prompt)
            personalized_description = response.text

            recommendations.append((job_title, similarity, personalized_description))

        return recommendations

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)
