import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Content_Generator:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("groq_api_key"), model_name="llama-3.1-70b-versatile")

    def extract_job_information(self, job_page_content):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {job_page_content}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website or a job post. 
            Extract job postings from the input text and return them in valid JSON format with the following keys: `job_role`, `job_experience`, `required_skills`, `job_description`, `job_salary`, `company_culture`, `company_info`, `is_job_post`. If any key has no data, set its value to `None`. Set `is_job_post` to `true` if it's a valid job post, otherwise `false` and also add a key `reason` to know the actual reason make sure it does not sound like this was done by automated script. 
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"job_page_content": job_page_content})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def compare_resume_with_job_post(self, job_post, resume_content):
        resume_content_prompt = PromptTemplate.from_template("""
            ### JSON data representing a job post
            {job_post}

            ### INSTRUCTION:
            Compare the provided JSON data representing a job post with the accompanying resume content below. {resume_content}

            1. Analysis:

            Identify and describe the similarities and differences between the job post and the resume.
            Highlight specific strengths of the applicant that align with the job requirements.
            Identify any areas for improvement where the applicant may not fully meet the expectations.
            
            Insights:

            2. Based on your analysis, assess the overall fit of the applicant for the role.
            Provide specific examples or quotes from both the job post and the resume to support your conclusions.
            
            3. Resume Improvements:

            Suggest specific changes or enhancements to the resume that could better align it with the job post and improve the candidate’s chances of securing an interview.

            4. Recommendation:

            Conclude with a recommendation on whether the applicant is suitable for the position and any next steps that could enhance their application.
            
            Resume Improvements:

           ### (NO PREAMBLE):
            """
            )
                
        resume_extract = resume_content_prompt | self.llm
        resume_content_output = resume_extract.invoke(input={"job_post": job_post, "resume_content":resume_content })
        return resume_content_output.content

if __name__ == "__main__":
    print("hi")