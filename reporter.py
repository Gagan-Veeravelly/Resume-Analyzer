"""
reporter.py
Generates a formatted summary report in the terminal
and saves it as a .txt file.
"""

import os
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    USE_COLOR = True
except ImportError:
    USE_COLOR = False

def c(text, color):
    if not USE_COLOR:
        return text
    colors = {
        'gold':  Fore.YELLOW,
        'green': Fore.GREEN,
        'red':   Fore.RED,
        'cyan':  Fore.CYAN,
        'blue':  Fore.BLUE,
        'bold':  Style.BRIGHT,
        'dim':   Style.DIM,
    }
    return colors.get(color, '') + str(text) + Style.RESET_ALL

def level_color(level):
    return {
        "Fresher / Intern": 'cyan',
        "Junior":           'green',
        "Mid-Level":        'blue',
        "Senior":           'gold',
        "Expert / Lead":    'red',
    }.get(level, 'bold')

def score_bar(score, width=30):
    filled = int(score / 100 * width)
    bar = '█' * filled + '░' * (width - filled)
    color = 'green' if score >= 70 else 'gold' if score >= 45 else 'red'
    return c(bar, color) + f'  {score}/100'

def generate_report(parsed, score_data=None):
    """Print a formatted report to terminal and return as plain text string."""
    lines = []
    def p(text=''):
        print(text)
        # Strip color codes for file
        clean = text
        for code in ['\x1b[0m','\x1b[1m','\x1b[2m','\x1b[33m','\x1b[32m',
                     '\x1b[31m','\x1b[36m','\x1b[34m','\x1b[35m']:
            clean = clean.replace(code, '')
        lines.append(clean)

    DIVIDER = c('═' * 60, 'dim')
    p(DIVIDER)
    p(c('          RESUME PARSER & ANALYZER — REPORT', 'gold'))
    p(c(f'          Generated: {datetime.now().strftime("%d %b %Y, %I:%M %p")}', 'dim'))
    p(DIVIDER)

    # Contact
    ct = parsed['contact']
    p(c('\n👤  CANDIDATE', 'bold'))
    p(f"   Name     : {c(ct['name'], 'gold')}")
    p(f"   Email    : {ct['email']}")
    p(f"   Phone    : {ct['phone']}")
    p(f"   LinkedIn : {ct['linkedin']}")
    p(f"   GitHub   : {ct['github']}")

    # Experience Level
    level = parsed['level']
    p(c('\n📊  EXPERIENCE LEVEL', 'bold'))
    p(f"   {c('[ ' + level + ' ]', level_color(level))}   —   "
      f"{parsed['experience']['total_years']} year(s) estimated")

    # Skills
    p(c('\n🛠   TECHNICAL SKILLS', 'bold'))
    for category, skills in parsed['skills']['technical'].items():
        p(f"   {c(category + ':', 'cyan')}")
        p(f"     {', '.join(skills)}")

    if parsed['skills']['soft']:
        p(c('\n🤝  SOFT SKILLS', 'bold'))
        p(f"   {', '.join(parsed['skills']['soft'])}")

    # Experience
    p(c('\n💼  EXPERIENCE ENTRIES', 'bold'))
    entries = parsed['experience']['entries']
    if entries:
        for i, e in enumerate(entries[:5], 1):
            p(f"   {i}. {c(e['date_range'], 'gold')}  ({e['years']} yr{'s' if e['years']!=1 else ''})")
    else:
        p(c('   No date ranges detected', 'dim'))

    # Education
    p(c('\n🎓  EDUCATION', 'bold'))
    edu = parsed['education']
    if edu:
        for e in edu[:4]:
            p(f"   • {e['text'][:80]}  [{e['year']}]")
    else:
        p(c('   No education entries detected', 'dim'))

    # JD Score
    if score_data:
        p(c('\n🎯  JOB DESCRIPTION MATCH', 'bold'))
        p(f"   Overall Score  : {score_bar(score_data['overall_score'])}")
        p(f"   Skill Match    : {score_bar(score_data['skill_score'])}")
        p(f"   Keyword Match  : {score_bar(score_data['keyword_score'])}")
        p(f"   Experience Fit : {score_bar(score_data['experience_score'])}")

        if score_data['matched_skills']:
            p(c('\n   ✅ Matched Skills:', 'green'))
            p(f"      {', '.join(score_data['matched_skills'])}")
        if score_data['missing_skills']:
            p(c('\n   ❌ Missing Skills:', 'red'))
            p(f"      {', '.join(score_data['missing_skills'][:10])}")

    p('\n' + DIVIDER)
    return '\n'.join(lines)

def save_report(report_text, output_dir='reports'):
    """Save the report as a .txt file in the reports/ folder."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(output_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"\n📁  Report saved → {path}")
    return path