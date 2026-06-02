# Resume Parser & Analyzer

Extracts key information from resumes (PDF/DOCX) using Python.

## Features
- Extract skills, experience, education
- Score resumes against job descriptions
- Generate summary reports (terminal + saved .txt)
- Categorize by experience level

## Tech Stack
- Python 3.x
- textract-style dispatcher (PyPDF2 + python-docx)
- regex for pattern matching
- NLTK for tokenization and stopwords

## Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

## Usage
python main.py                        # runs with sample data
python main.py resume.pdf            # your resume
python main.py resume.pdf jd.txt     # resume + job description