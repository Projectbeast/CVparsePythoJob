from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from utils.text_processing import preprocess_text
from utils.resume_parser import parse_resume
import json
import os
import requests


import numpy as np

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

class JobMatcher:
    def __init__(self, job_listings_path=None):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        if job_listings_path:
            self.jobs_df = pd.read_csv(job_listings_path)
            self.jobs_df['processed_description'] = self.jobs_df['description'].apply(preprocess_text)
            self.job_embeddings = self.model.encode(self.jobs_df['processed_description'].tolist())

        # Initialize Gemini
        genai.configure(api_key='AIzaSyAQyxQ3i3LhU_ocwWN7kHe7CwRjIRVsbBw')
        self.gemini = genai.GenerativeModel('gemini-pro')

    def process_resume(self, resume_file):
        resume_text = parse_resume(resume_file)
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
            prompt = f"""
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
            #response = self.gemini.generate_content(prompt)
            response=get_job_suggestions_MistralAI(prompt);
            #response_data = json.loads(response)
            response_data = response['choices'][0]['message']['content']
            personalized_description  = response_data

            recommendations.append((job_title, similarity, personalized_description))
            #return jsonify({"message": "File uploaded successfully", "text": recommendations}), 200
            #return jsonify({"message": "File uploaded successfully", "recommendations": recommendations}), 200
            #print(recommendations);
        return recommendations

    def match_candidates(self, job_description, resumes):
        processed_job = preprocess_text(job_description)
        job_embedding = self.model.encode([processed_job])[0]

        processed_resumes = [preprocess_text(resume["name"]) for resume in resumes]
        resume_embeddings = self.model.encode(processed_resumes)

        similarities = cosine_similarity([job_embedding], resume_embeddings)[0]
        top_indices = similarities.argsort()[-5:][::-1]

        matches = []
        for idx in top_indices:
            resume = resumes[idx]
            similarity = float(similarities[idx])

            # Use Gemini to generate a match summary
            prompt = f"Based on the following job description and resume, provide a concise summary of why this candidate might be a good match:\n\nJob Description: {job_description}\n\nResume: {resume}"
            #response = self.gemini.generate_content(prompt)

            response=get_job_suggestions_MistralAI(prompt);
           
            response_data = response['choices'][0]['message']['content']
            match_summary = response_data

            #matches.append((resume, similarity, match_summary))

              # Append a dictionary instead of a tuple
            matches.append({
                "Candidatenaame":"K Bharathi  Dasan",
                "similarity": round(similarity,3),
                "match_summary":match_summary
            })
        
        matches = convert_sets_to_lists(matches)
        print(matches)    
        # Convert the matches list to JSON
        matches_json = json.dumps(matches, indent=4)  # `indent=4` for pretty printing
        return matches_json

#@app.route('/api/match-candidates', methods=['POST'])
@app.route('/api/upload_job_description', methods=['POST'])
def upload_job_description():
     # Check if the file part is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']  # Access the uploaded file

    if file and file.filename.endswith('.json'):
        # Read the file and decode it to get the JSON content
        file_content = file.read().decode('utf-8')
    try:
            # Load the JSON data from the file content
        json_data = json.loads(file_content)

            # Extract job_description and resumes from the JSON data
        job_description = json_data.get('job_description')
        resumes = json_data.get('resumes')

        if not job_description or not resumes:
                return jsonify({"error": "Missing job_description or resumes in the JSON file"}), 400
        
            #for resume in json_data["resumes"]:
        response=  job_matcher.match_candidates(job_description,resumes)
        response2=convert_sets_to_lists(response)

            # Do something with the extracted data
        return jsonify(response2
            ), 200

    except json.JSONDecodeError:
             return jsonify({"error": "Invalid JSON file"}), 400
    else:
     return jsonify({"error": "Please upload a valid JSON file"}), 400


# Create a JobMatcher instance (you can specify a CSV file for job listings if needed)
job_matcher = JobMatcher("data/job_listings.csv")  # Optionally pass a job_listings_path





def convert_sets_to_lists(data):
    if isinstance(data, set):
        return list(data)  # Converting set to list
    elif isinstance(data, dict):
        return {key: convert_sets_to_lists(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_sets_to_lists(item) for item in data]
    return data

@app.route('/api/match-resume', methods=['POST'])

def match_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Check for valid file formats
    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        # Process the extracted text
        recommendations = job_matcher.process_resume(file)

        # Example recommendation tuples
        # recommendations.append((job_title, similarity, personalized_description))
        # Ensure the recommendation tuples are converted to JSON-serializable dictionaries

        recommendations_list = []
        for job_title, similarity, personalized_description in recommendations:
            # Convert similarity (if it's numpy type) to native float
            if isinstance(similarity, (np.float32, np.float64)):
                similarity = float(similarity)

            # Build a dictionary for each recommendation
            recommendation_dict = {
                "id":"01",
                "company":"Cognizant Technology Solutions",
                "location":"Chennai",
                "salary":"100000",
                "title": job_title,
                "similarityScore": round(similarity,3),  # should be a standard float
                "personalized_description": personalized_description
            }
            recommendations_list.append(recommendation_dict)



        # Save the recommendations to a JSON file
        output_file_name = os.path.join(os.getcwd(), 'job_matches.json')
        save_to_json_file(recommendations_list, output_file_name)


        # Return the JSON response
        return jsonify({
            "message": "File uploaded successfully",
            "recommendations": recommendations_list
        }), 200
    else:
        return jsonify({"error": "File format not supported. Please upload a PDF or DOCX file."}), 400


# Function to save recommendations to a JSON file
def save_to_json_file(data, file_name):
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)


# def match_resume():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     # Check for valid file formats
#     if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
#         # Process the extracted text
#         recommendations = job_matcher.process_resume(file)
#         return jsonify({"message": "File uploaded successfully", "recommendations": recommendations}), 200
#     else:
#         return jsonify({"error": "File format not supported. Please upload a PDF or DOCX file."}), 400





#--------------Match
# Mock data for job matches and available job IDs
job_matches = [
    {
        "id": "1", 
        "title": "Software Engineer", 
        "company": "TechCorp", 
        "location": "New York", 
        "salary": "$120,000", 
        "similarityScore": "85%"
    },
    {
        "id": "2", 
        "title": "Data Scientist", 
        "company": "DataWorks", 
        "location": "San Francisco", 
        "salary": "$140,000", 
        "similarityScore": "90%"
    },
]

available_job_ids = {
    "job_ids": ["1", "2", "3", "4", "5"]
}


# Route for job matches
# @app.route('/api/job_matches', methods=['GET'])
# def get_job_matches():
#     return jsonify(job_matches)


# Route to read job matches from a JSON file
@app.route('/api/job_matches', methods=['GET'])
def get_job_matches():
    # Read the JSON file
    try:
        with open('job_matches.json', 'r') as file:
            job_matches = json.load(file)
        return jsonify(job_matches)
    except FileNotFoundError:
        return jsonify({"error": "Job matches file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500


# Route for available job IDs
@app.route('/api/available_job_ids', methods=['GET'])
def get_available_job_ids():
    return jsonify(available_job_ids)


#---Job Details

# Mock data for job details and fit analysis
job_data = {
    "1": {
        "analysis": {
            "job_details": {
                "job_title": "Software Engineer",
                "company_name": "TechCorp",
                "location": "New York",
                "salary": "$120,000",
                "key_responsibilities": "Developing and maintaining software applications."
            },
            "fit_analysis": {
                "overall_suitability_score": "85%",
                "candidate_strengths": "Strong programming skills, team player",
                "areas_for_improvement": "Needs experience in cloud technologies",
                "detailed_analysis": "Candidate has 85% match in required skills and experience."
            }
        }
    },
    "2": {
        "analysis": {
            "job_details": {
                "job_title": "Data Scientist",
                "company_name": "DataWorks",
                "location": "San Francisco",
                "salary": "$140,000",
                "key_responsibilities": "Analyze data to generate actionable insights."
            },
            "fit_analysis": {
                "overall_suitability_score": "90%",
                "candidate_strengths": "Excellent statistical and analytical skills",
                "areas_for_improvement": "Needs more experience with deep learning frameworks",
                "detailed_analysis": "Candidate has a 90% match with strong analytics background."
            }
        }
    }
}

# Route for fetching job details and fit analysis by job ID
@app.route('/api/job_details/<job_id>', methods=['GET'])
def get_job_details(job_id):
    if job_id in job_data:
        return jsonify(job_data[job_id])
    else:
        return jsonify({"error": "Job not found"}), 404


# if __name__ == '__main__':
#     app.run(debug=True, port=5000)



def get_job_suggestions_MistralAI(resume_content, bearer_token="9wXP4xfyD1kxegptM8PN8vt2sQV7HIKu"):
    # API endpoint
    url = "https://api.mistral.ai/v1/chat/completions"

    # Define the headers for the request
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Define the request payload
    data = data = {
    "model": "mistral-large-latest",
    "temperature": 0.7,
    "top_p": 1,
    "max_tokens": 500,
    "stream": False,
    "random_seed": 0,
    "messages": [
        {
            "role": "user",
            "content": f"{resume_content}"  # Corrected line
        }
    ],
    "response_format": {
        "type": "text"
    },
    "safe_prompt": False
}

    # Make the POST request to the API
    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the response JSON
        return response.json()
    else:
        # Raise an error if the request failed
        raise Exception(f"Error: {response.status_code} - {response.text}")

