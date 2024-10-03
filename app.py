# import streamlit as st
# from pages import candidate_page, employer_page
# import nltk

# nltk.download('punkt', quiet=True)
# nltk.download('stopwords', quiet=True)

# def main():
#     st.sidebar.title("Job Matcher")
#     page = st.sidebar.radio("Select Page", ["Candidate", "Employer"])

#     if page == "Candidate":
#         candidate_page.show()
#     elif page == "Employer":
#         employer_page.show()

# if __name__ == "__main__":
#     main()


# How to run this app
# streamlit run d:/NFC/AI/PythonRECAPI/job/app.py
# https://ai.google.dev/gemini-api/docs/api-key
# https://aistudio.google.com/app/apikey
# Google GEN AI API KEy-> AIzaSyAQyxQ3i3LhU_ocwWN7kHe7CwRjIRVsbBw

import nltk

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
from flask import Flask

# Import your CandidatService (API routes)
from VetorDBSathish import jobmatcherAPI  # Import the entire module to load routes


# If CandidatService.py contains route definitions, you should import them here or
# register the blueprints if you are using them.
# For example:
# app.register_blueprint(CandidatService.some_blueprint)

if __name__ == '__main__':
    jobmatcherAPI.app.run(debug=True, port=5000)