"""
app.py
Flask Web Server for Resume Parser & Analyzer
Run locally: python app.py
Run on cloud: gunicorn app:app
"""
import os
import tempfile
import re
import nltk
from flask import Flask, request, render_template, jsonify

# 🔹 Ensure NLTK data is downloaded on first run
for resource in ['punkt', 'stopwords']:
    try:
        nltk.data.find(f'tokenizers/{resource}')
    except LookupError:
        nltk.download(resource, quiet=True)

# 🔹 Import your existing modules
from resume_parser import ResumeParser
from scorer import score_resume
from reporter import generate_report

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

def strip_ansi(text):
    """Remove ANSI terminal color codes for clean web display"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', str(text))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'success': False, 'error': 'No resume file uploaded'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    jd_text = request.form.get('jd', '').strip()

    # Create a secure temporary file path
    temp_dir = tempfile.gettempdir()
    safe_filename = f"upload_{os.urandom(4).hex()}_{file.filename}"
    temp_path = os.path.join(temp_dir, safe_filename)

    try:
        file.save(temp_path)
        
        # 1. Parse Resume
        parser = ResumeParser(filepath=temp_path)
        parsed = parser.parse()
        
        # 2. Score against JD (if provided)
        score_data = score_resume(parsed, jd_text) if jd_text else None
        
        # 3. Generate Report
        report = generate_report(parsed, score_data)
        
        # 4. Clean terminal colors & return JSON
        clean_report = strip_ansi(report) if report else "Analysis complete."
        return jsonify({'success': True, 'report': clean_report})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    finally:
        # Always clean up the uploaded file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    # Cloud platforms inject the PORT env variable. Local fallback: 5000
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🌐 Resume Analyzer running on http://0.0.0.0:{port}")
    print("👉 Open http://127.0.0.1:5000 in your browser\n")
    
    # Set debug=True for local development, debug=False for production
    app.run(host='0.0.0.0', port=port, debug=True)