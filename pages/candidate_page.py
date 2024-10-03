import streamlit as st
from job_matcher import JobMatcher

def show():
    st.title("Candidate Job Matcher")

    # File uploader for resume
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file is not None:
        # Initialize JobMatcher
        job_matcher = JobMatcher("data/job_listings.csv")

        # Process the resume and get recommendations
        recommendations = job_matcher.process_resume(uploaded_file)

        # Display recommendations
        st.subheader("Top Job Recommendations:")
        for i, (job_title, similarity, description) in enumerate(recommendations, 1):
            st.write(f"{i}. {job_title}")
            st.write(f"Similarity: {similarity * 100:.2f}%")
            st.write(f"   Description: {description}")
            st.write("---")
