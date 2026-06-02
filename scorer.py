"""
scorer.py
Scores a parsed resume against a job description using
keyword overlap, skill matching, and experience weighting.
"""

import re
from resume_parser import SKILLS_DB, SOFT_SKILLS, _safe_word_tokenize, _get_stopwords

def extract_jd_keywords(jd_text):
    """Pull meaningful keywords from the job description."""
    stop = _get_stopwords()
    tokens = _safe_word_tokenize(jd_text.lower())
    keywords = [t for t in tokens if t.isalpha() and t not in stop and len(t) > 2]
    return set(keywords)

def extract_jd_skills(jd_text):
    """Find all known skills mentioned in the JD."""
    found = []
    all_skills = [s for cat in SKILLS_DB.values() for s in cat] + SOFT_SKILLS
    for skill in all_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', jd_text, re.IGNORECASE):
            found.append(skill)
    return found

def extract_jd_years(jd_text):
    """Extract minimum years of experience required from JD."""
    match = re.search(r'(\d+)\+?\s*years?\s*(of\s+)?(experience|exp)', jd_text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def score_resume(parsed_data, jd_text):
    """
    Returns a score dict with:
      - overall_score (0-100)
      - skill_score, keyword_score, experience_score
      - matched_skills, missing_skills
    """
    # ── Skill Match ──────────────────────────────────────────────────────────
    jd_skills   = extract_jd_skills(jd_text)
    resume_skills_flat = [
        s for cat in parsed_data['skills']['technical'].values() for s in cat
    ] + parsed_data['skills']['soft']

    resume_skills_lower = {s.lower() for s in resume_skills_flat}
    jd_skills_lower     = {s.lower() for s in jd_skills}

    matched  = [s for s in jd_skills if s.lower() in resume_skills_lower]
    missing  = [s for s in jd_skills if s.lower() not in resume_skills_lower]

    skill_score = round((len(matched) / len(jd_skills) * 100) if jd_skills else 50)

    # ── Keyword Match ────────────────────────────────────────────────────────
    jd_keywords     = extract_jd_keywords(jd_text)
    resume_keywords = set(_safe_word_tokenize(parsed_data.get('_raw','').lower()))
    # Use resume word count as proxy if raw not stored
    if not resume_keywords:
        resume_keywords = {s.lower() for s in resume_skills_flat}

    common = jd_keywords & resume_keywords
    keyword_score = round((len(common) / len(jd_keywords) * 100) if jd_keywords else 50)
    keyword_score = min(keyword_score, 100)

    # ── Experience Match ─────────────────────────────────────────────────────
    required_years   = extract_jd_years(jd_text)
    candidate_years  = parsed_data['experience']['total_years']
    if required_years == 0:
        exp_score = 70
    elif candidate_years >= required_years:
        exp_score = 100
    elif candidate_years >= required_years * 0.7:
        exp_score = 75
    else:
        exp_score = max(10, int(candidate_years / required_years * 100))

    # ── Overall ──────────────────────────────────────────────────────────────
    overall = round(skill_score * 0.5 + keyword_score * 0.3 + exp_score * 0.2)

    return {
        "overall_score":    overall,
        "skill_score":      skill_score,
        "keyword_score":    keyword_score,
        "experience_score": exp_score,
        "matched_skills":   matched,
        "missing_skills":   missing,
        "jd_required_years": required_years,
    }