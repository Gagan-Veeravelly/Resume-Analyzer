"""
resume_parser.py
Core module: extracts text from PDF/DOCX and parses
skills, experience, education using regex + NLTK basics.
"""

import re
import os
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

def _safe_word_tokenize(text):
    try:
        return word_tokenize(text)
    except LookupError:
        return re.findall(r'\b\w+\b', text)

def _safe_sent_tokenize(text):
    try:
        return sent_tokenize(text)
    except LookupError:
        return re.split(r'(?<=[.!?])\s+', text)

def _get_stopwords():
    try:
        return set(stopwords.words('english'))
    except LookupError:
        return {'i','me','my','we','our','you','he','she','they','it',
                'the','a','an','and','or','but','in','on','at','to','for',
                'of','with','by','from','is','are','was','were','be','been'}

def extract_text_from_pdf(filepath):
    import PyPDF2
    text = ""
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    return text.strip()

def extract_text_from_docx(filepath):
    from docx import Document
    doc = Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_text(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext == '.docx':
        return extract_text_from_docx(filepath)
    elif ext == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")

EMAIL_RE      = re.compile(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}')
PHONE_RE      = re.compile(r'(\+?\d[\d\s\-().]{7,}\d)')
LINKEDIN_RE   = re.compile(r'linkedin\.com/in/[\w\-]+', re.IGNORECASE)
GITHUB_RE     = re.compile(r'github\.com/[\w\-]+', re.IGNORECASE)
YEAR_RE       = re.compile(r'\b(19|20)\d{2}\b')
DATE_RANGE_RE = re.compile(
    r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?((?:19|20)\d{2})'
    r'\s*[-–—to]+\s*'
    r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?((?:19|20)\d{2}|Present|present|Current|current)',
    re.IGNORECASE
)
DEGREE_RE = re.compile(
    r'\b(B\.?Tech|B\.?E\.?|B\.?Sc?\.?|B\.?A\.?|M\.?Tech|M\.?E\.?|M\.?Sc?\.?'
    r'|M\.?A\.?|MBA|MCA|BCA|Ph\.?D\.?|Bachelor[s]?|Master[s]?|Diploma|Associate)\b',
    re.IGNORECASE
)

SKILLS_DB = {
    "Programming Languages": [
        "Python","Java","JavaScript","TypeScript","C","C++","C#",
        "Go","Rust","Ruby","PHP","Swift","Kotlin","Scala","R",
        "MATLAB","Perl","Shell","Bash","SQL","HTML","CSS"
    ],
    "Frameworks & Libraries": [
        "Django","Flask","FastAPI","React","Angular","Vue","Node.js",
        "Spring","TensorFlow","PyTorch","Keras","Scikit-learn",
        "Pandas","NumPy","Matplotlib","NLTK","OpenCV","Bootstrap",".NET"
    ],
    "Databases": [
        "MySQL","PostgreSQL","MongoDB","SQLite","Oracle","Redis",
        "Cassandra","DynamoDB","Firebase","Elasticsearch"
    ],
    "Cloud & DevOps": [
        "AWS","Azure","GCP","Docker","Kubernetes","Jenkins",
        "Git","GitHub","GitLab","CI/CD","Terraform","Linux"
    ],
    "Tools & Platforms": [
        "VS Code","Jira","Postman","Figma","Tableau","Power BI",
        "Excel","Jupyter","Hadoop","Spark","Kafka"
    ],
    "Concepts": [
        "Machine Learning","Deep Learning","NLP","REST","Microservices",
        "OOP","Agile","Scrum","DevOps","Data Structures","Algorithms"
    ]
}

SOFT_SKILLS = [
    "Leadership","Communication","Teamwork","Problem-solving","Critical thinking",
    "Time management","Adaptability","Creativity","Collaboration","Analytical"
]

class ResumeParser:
    def __init__(self, filepath=None, text=None):
        if filepath:
            self.raw_text = extract_text(filepath)
        elif text:
            self.raw_text = text
        else:
            raise ValueError("Provide filepath or text.")
        self.lines     = self.raw_text.splitlines()
        self.tokens    = _safe_word_tokenize(self.raw_text)
        self.sentences = _safe_sent_tokenize(self.raw_text)

    def extract_contact(self):
        email    = EMAIL_RE.search(self.raw_text)
        phone    = PHONE_RE.search(self.raw_text)
        linkedin = LINKEDIN_RE.search(self.raw_text)
        github   = GITHUB_RE.search(self.raw_text)
        name = "Not found"
        for line in self.lines[:8]:
            line = line.strip()
            if line and len(line.split()) <= 5 and re.match(r'^[A-Za-z\s.\-]+$', line):
                name = line
                break
        return {
            "name":     name,
            "email":    email.group()    if email    else "Not found",
            "phone":    phone.group()    if phone    else "Not found",
            "linkedin": linkedin.group() if linkedin else "Not found",
            "github":   github.group()   if github   else "Not found",
        }

    def extract_skills(self):
        found = {}
        for category, skills_list in SKILLS_DB.items():
            matched = [s for s in skills_list
                       if re.search(r'\b' + re.escape(s) + r'\b', self.raw_text, re.IGNORECASE)]
            if matched:
                found[category] = matched
        soft = [s for s in SOFT_SKILLS
                if re.search(r'\b' + re.escape(s) + r'\b', self.raw_text, re.IGNORECASE)]
        return {"technical": found, "soft": soft}

    def extract_experience(self):
        entries, durations = [], []
        for match in DATE_RANGE_RE.finditer(self.raw_text):
            start_yr = int(match.group(2))
            end_raw  = match.group(4)
            end_yr   = 2024 if end_raw.lower() in ('present','current') else int(end_raw)
            duration = end_yr - start_yr
            context  = self.raw_text[max(0,match.start()-120):match.end()+80]
            context  = re.sub(r'\s+', ' ', context).strip()
            entries.append({"date_range": match.group(0).strip(), "years": duration, "context": context})
            durations.append(duration)
        total = sum(durations) if durations else self._estimate_years()
        return {"entries": entries, "total_years": total}

    def _estimate_years(self):
        years = [int(y) for y in YEAR_RE.findall(self.raw_text) if 1990 <= int(y) <= 2025]
        return max(years) - min(years) if len(years) >= 2 else 0

    def extract_education(self):
        seen, unique = set(), []
        for sent in self.sentences:
            if DEGREE_RE.search(sent):
                key = sent.strip()[:60]
                if key not in seen:
                    seen.add(key)
                    yr = YEAR_RE.search(sent)
                    unique.append({"text": sent.strip(), "year": yr.group() if yr else "N/A"})
        return unique

    def categorize_level(self, total_years):
        if total_years <= 1:   return "Fresher / Intern"
        elif total_years <= 3: return "Junior"
        elif total_years <= 6: return "Mid-Level"
        elif total_years <= 10: return "Senior"
        else:                  return "Expert / Lead"

    def parse(self):
        experience = self.extract_experience()
        return {
            "contact":    self.extract_contact(),
            "skills":     self.extract_skills(),
            "experience": experience,
            "education":  self.extract_education(),
            "level":      self.categorize_level(experience['total_years']),
            "word_count": len(self.tokens)
        }