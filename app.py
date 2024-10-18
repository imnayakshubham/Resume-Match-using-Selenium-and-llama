import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from content_generator import Content_Generator
from dotenv import load_dotenv

load_dotenv()
import re

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]*?>', '', text)
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s{2,}', ' ', text)
    # Trim leading and trailing whitespace
    text = text.strip()
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text
    
        
def create_streamlit_app(llm):
    # Title of the app
    st.title("Resume Match")

    # Input for URL
    url = st.text_input("Enter a Job Post URL:", placeholder="https://example.com")

    # Text area for additional content
    resume_content = st.text_area("Enter your Resume content:")

    # Function to enable the submit button
    def enable_submit():
        return url and resume_content

    # Submit button
    if st.button("Submit", disabled=not enable_submit()):
        if url and resume_content:
            with st.spinner("Processing you input please wait..."):
                loader = WebBaseLoader(url)
                data = clean_text(loader.load().pop().page_content)
                job_post_infos = llm.extract_job_information(data)
                for job_post_info in job_post_infos:
                    is_job_post_true = job_post_info.get('is_job_post', False)
                    if(is_job_post_true):
                        result = llm.compare_resume_with_job_post(job_post_info,resume_content)
                        st.markdown(result)
                    else:
                        st.warning(job_post_info.get('reason', "This entry is not a job post."))
            
    else:
        if not enable_submit():
            st.warning("Please fill both fields to enable the submit button.")


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Resume Match", page_icon="❤️")
    llm = Content_Generator()
    create_streamlit_app(llm)