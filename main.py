"""
main.py
Entry point — run this file to use the Resume Analyzer.
Usage:
  python main.py                        # interactive mode
  python main.py resume.pdf            # analyze a file
  python main.py resume.pdf jd.txt     # analyze + score vs JD
"""

import sys
import os
from resume_parser import ResumeParser
from scorer import score_resume
from reporter import generate_report, save_report

SAMPLE_RESUME = """
John Doe
john.doe@email.com | +91-9876543210 | linkedin.com/in/johndoe | github.com/johndoe

SUMMARY
Experienced Software Engineer with 5 years of hands-on experience in Python,
Django, and cloud technologies. Strong problem-solving and communication skills.

SKILLS
Programming: Python, JavaScript, SQL, HTML, CSS
Frameworks: Django, Flask, React, Node.js
Databases: MySQL, PostgreSQL, MongoDB
Tools: Git, GitHub, Docker, AWS, Jupyter, VS Code
Concepts: REST, OOP, Agile, Machine Learning, NLP

EXPERIENCE
Software Engineer — TechCorp Solutions
Jan 2021 – Present
- Built REST APIs using Django and Flask
- Deployed microservices on AWS using Docker

Junior Developer — StartupXYZ
Jun 2019 – Dec 2020
- Developed frontend features using React and JavaScript
- Worked with PostgreSQL and MongoDB databases

EDUCATION
B.Tech in Computer Science — JNTU Hyderabad, 2019
"""

SAMPLE_JD = """
We are looking for a Senior Python Developer with:
- 4+ years of experience in Python and Django
- Strong knowledge of REST APIs and Microservices
- Experience with AWS, Docker, and Kubernetes
- Familiarity with React or any frontend framework
- Good communication and teamwork skills
- Knowledge of Machine Learning is a plus
"""

def run(resume_path=None, jd_path=None):
    print("\n🔍  Resume Parser & Analyzer")
    print("    Tech: Python | regex | NLTK | PyPDF2 | python-docx\n")

    # Load resume
    if resume_path:
        print(f"📄  Loading: {resume_path}")
        parser = ResumeParser(filepath=resume_path)
    else:
        print("📄  No file provided — using sample resume text\n")
        parser = ResumeParser(text=SAMPLE_RESUME)

    # Parse
    print("⚙️   Parsing resume...")
    parsed = parser.parse()

    # Load JD
    score_data = None
    if jd_path:
        with open(jd_path, 'r') as f:
            jd_text = f.read()
        print("📋  Scoring against job description...")
        score_data = score_resume(parsed, jd_text)
    else:
        print("📋  No JD provided — scoring against sample JD\n")
        score_data = score_resume(parsed, SAMPLE_JD)

    # Report
    report = generate_report(parsed, score_data)
    save_report(report)

if __name__ == '__main__':
    args = sys.argv[1:]
    resume_path = args[0] if len(args) > 0 else None
    jd_path     = args[1] if len(args) > 1 else None
    run(resume_path, jd_path)