import re
from collections import Counter

STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "this", "that",
    "from", "will", "have", "has", "had", "was", "were", "who", "what", "when",
    "where", "how", "all", "any", "can", "able", "ability", "job", "role",
    "work", "working", "experience", "required", "requirements", "preferred",
    "candidate", "responsibilities", "including", "using", "use", "years", "year",
    "good", "strong", "excellent", "must", "should", "into", "about", "such",
    "their", "them", "they", "will", "not", "our", "you", "also", "more"
}

SKILL_ALIASES = {
    "js": "javascript", "py": "python", "postgres": "postgresql",
    "nodejs": "node.js", "node js": "node.js", "reactjs": "react",
    "nextjs": "next.js", "vuejs": "vue", "ts": "typescript",
    "golang": "go", "k8s": "kubernetes", "tf": "terraform",
    "machine-learning": "machine learning", "ml": "machine learning",
    "deep-learning": "deep learning", "dl": "deep learning",
    "ms excel": "excel", "c sharp": "c#", "dot net": ".net",
    "gcp": "google cloud", "aws": "aws", "tailwind": "tailwind css",
    "ci cd": "ci/cd", "cicd": "ci/cd", "restful": "rest api", "rest apis": "rest api"
}

KNOWN_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", ".net", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "dart", "r", "shell scripting", "bash",
    # Frontend Technologies
    "html", "css", "react", "next.js", "vue", "nuxt", "angular", "tailwind css", "bootstrap",
    "sass", "redux", "svelte", "webpack", "vite", "jquery",
    # Backend & Frameworks
    "node.js", "flask", "django", "fastapi", "express.js", "nest.js", "spring boot", "laravel",
    "ruby on rails", "asp.net", "rest api", "graphql", "grpc", "microservices", "websockets",
    # Databases & Caching
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis", "elasticsearch", "cassandra",
    "dynamodb", "oracle", "mariadb", "firebase", "supabase", "prisma", "sqlalchemy",
    # Cloud & DevOps
    "aws", "azure", "google cloud", "docker", "kubernetes", "git", "github", "gitlab",
    "ci/cd", "jenkins", "terraform", "ansible", "linux", "unix", "nginx", "apache", "prometheus",
    "grafana", "helm", "kafka", "rabbitmq", "celery", "airflow",
    # Data Science, AI & Machine Learning
    "machine learning", "deep learning", "data analysis", "data science", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "keras", "power bi", "tableau", "excel",
    "nlp", "computer vision", "llm", "langchain", "hugging face", "opencv", "spark", "hadoop",
    # Mobile Development
    "flutter", "react native", "ios", "android",
    # Architecture, Methodologies & Quality
    "agile", "scrum", "oop", "data structures", "algorithms", "problem solving",
    "communication", "teamwork", "leadership", "project management", "testing", "pytest",
    "unit testing", "jest", "selenium", "cypress", "cybersecurity", "networking", "figma"
]

def normalize(text):
    text = (text or "").lower()
    for alias, canonical in SKILL_ALIASES.items():
        text = re.sub(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", canonical, text)
    return re.sub(r"\s+", " ", text).strip()

def contains_term(text, term):
    # Word boundaries prevent "java" from matching "javascript".
    pattern = r"(?<![a-z0-9+#.])" + re.escape(term.lower()) + r"(?![a-z0-9+#.])"
    return bool(re.search(pattern, text.lower()))

def extract_keywords(job_description):
    normalized = normalize(job_description)
    found_skills = [skill for skill in KNOWN_SKILLS if contains_term(normalized, skill)]
    tokens = re.findall(r"[a-z][a-z0-9+#.-]{2,}", normalized)
    common = Counter(token for token in tokens if token not in STOPWORDS)
    extra_keywords = [word for word, _ in common.most_common(20)
                      if word not in found_skills and len(word) > 3]
    return list(dict.fromkeys(found_skills + extra_keywords[:12]))

def score_resume_structure(text):
    headings = ["education", "skills", "projects", "experience", "work experience",
                "professional summary", "summary", "certifications", "achievements"]
    found = [heading for heading in headings if re.search(r"\b" + re.escape(heading) + r"\b", text, re.I)]
    score = round(min(100, len(found) / 6 * 100))
    return score, found

def analyze_resume(resume_text, job_description, job_title=""):
    resume = normalize(resume_text)
    job = normalize(job_description)
    keywords = extract_keywords(job_description)
    matched = [word for word in keywords if contains_term(resume, word)]
    missing = [word for word in keywords if word not in matched]
    keyword_score = round(100 * len(matched) / max(1, len(keywords)))

    title_terms = [t for t in re.findall(r"[a-z][a-z+#.]{2,}", normalize(job_title)) if t not in STOPWORDS]
    title_hits = sum(contains_term(resume, term) for term in title_terms)
    title_score = round(100 * title_hits / max(1, len(title_terms))) if title_terms else keyword_score
    job_skills = [s for s in KNOWN_SKILLS if contains_term(job, s)]
    skill_hits = sum(s in matched for s in job_skills)
    skills_score = round(100 * skill_hits / max(1, len(job_skills))) if job_skills else keyword_score
    title_skill_score = round(0.4 * title_score + 0.6 * skills_score)

    structure_score, found_headings = score_resume_structure(resume_text)
    word_count = len(re.findall(r"\b\w+\b", resume_text))
    formatting_score = 100
    formatting_notes = []
    if "\t" in resume_text:
        formatting_score -= 10
        formatting_notes.append("Tabs may indicate layout that could parse inconsistently.")
    if len(re.findall(r"[|]{2,}|[_]{4,}", resume_text)) > 2:
        formatting_score -= 15
        formatting_notes.append("Avoid decorative separators and long underscore lines.")
    if word_count < 120:
        formatting_score -= 25
        formatting_notes.append("Very short extracted text; check that the full resume was parsed.")
    if word_count > 1100:
        formatting_score -= 15
        formatting_notes.append("Resume may be longer than necessary for many entry-level roles.")
    formatting_score = max(0, formatting_score)

    email_present = bool(re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", resume_text, re.I))
    phone_present = bool(re.search(r"(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13})", resume_text))
    linkedin_present = "linkedin.com" in resume
    github_present = "github.com" in resume
    contact_parts = [email_present, phone_present, linkedin_present or github_present]
    contact_score = round(100 * sum(contact_parts) / len(contact_parts))

    action_verbs = [
        "built", "developed", "created", "designed", "implemented", "improved",
        "managed", "analyzed", "automated", "delivered", "led", "optimized",
        "tested", "deployed", "reduced", "increased", "spearheaded", "architected",
        "engineered", "streamlined", "orchestrated", "resolved"
    ]
    action_hits = sum(contains_term(resume, verb) for verb in action_verbs)
    quantified = bool(re.search(r"\b\d+(\.\d+)?\s*(%|percent|users|customers|hours|days|projects|records|x)\b", resume))
    content_score = min(100, 45 + min(action_hits, 5) * 8 + (15 if quantified else 0))
    if word_count < 80:
        content_score = min(content_score, 35)

    edu_patterns = [
        r"\b(?:education|academic|qualifications|degree|diploma|university|college|school|graduated|coursework)\b",
        r"\b(?:bachelor|master|doctorate|phd|ph\.d|doctor of philosophy)\b",
        r"\b(?:b\.?tech|m\.?tech|bca|mca|bba|mba|b\.?sc|m\.?sc|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|b\.?e\.?|m\.?e\.?)\b"
    ]
    education_found = any(re.search(pattern, resume_text, re.I) for pattern in edu_patterns)
    experience_found = any(contains_term(resume, term) for term in ["experience", "internship", "employment", "worked", "projects"])
    education_experience_score = round((50 if education_found else 0) + (50 if experience_found else 0))

    dates = bool(re.search(r"\b(19|20)\d{2}\b", resume_text))
    consistency_score = 100 if dates else 65
    if word_count < 120:
        consistency_score = min(consistency_score, 60)

    factors = [
        {"name": "Keyword match", "weight": 25, "score": keyword_score,
         "explanation": f"{len(matched)} of {len(keywords)} detected job keywords appear in your resume."},
        {"name": "Job title and skills", "weight": 15, "score": title_skill_score,
         "explanation": "Compares the requested job title and recognized skills with your resume."},
        {"name": "Resume structure", "weight": 10, "score": structure_score,
         "explanation": f"Detected headings: {', '.join(found_headings) if found_headings else 'none of the standard headings'}."},
        {"name": "Formatting and readability", "weight": 10, "score": formatting_score,
         "explanation": "Uses extracted text length and simple layout indicators; it cannot inspect every visual layout issue."},
        {"name": "Contact details", "weight": 5, "score": contact_score,
         "explanation": f"Email: {'found' if email_present else 'missing'}, phone: {'found' if phone_present else 'missing'}, LinkedIn/GitHub: {'found' if linkedin_present or github_present else 'missing'}."},
        {"name": "Content quality", "weight": 10, "score": content_score,
         "explanation": f"Detected {action_hits} action verbs and {'quantified impact' if quantified else 'no clear quantified impact'}."},
        {"name": "Education and experience", "weight": 15, "score": education_experience_score,
         "explanation": f"Education section/details: {'detected' if education_found else 'not detected'}; experience/projects: {'detected' if experience_found else 'not detected'}."},
        {"name": "Length and consistency", "weight": 10, "score": consistency_score,
         "explanation": f"Extracted approximately {word_count} words; year/date indicator {'found' if dates else 'not found'}."},
    ]
    overall = round(sum(f["score"] * f["weight"] for f in factors) / 100)
    suggestions = []
    if missing:
        suggestions.append("Add relevant missing keywords only where they truthfully reflect your skills: " + ", ".join(missing[:12]) + ".")
    if not email_present:
        suggestions.append("Add a clearly readable email address.")
    if not phone_present:
        suggestions.append("Add a contact phone number.")
    if not linkedin_present and not github_present:
        suggestions.append("Add a professional LinkedIn or GitHub URL if you have one.")
    if structure_score < 70:
        suggestions.append("Use standard headings such as Summary, Skills, Education, Projects and Experience.")
    if not quantified:
        suggestions.append("Where truthful, describe project impact with numbers, outcomes or measurable results.")
    if word_count < 120:
        suggestions.append("Check that all resume sections were included and the file contains selectable text.")
    if formatting_notes:
        suggestions.extend(formatting_notes)
    if not suggestions:
        suggestions.append("Good baseline match. Review the job description and ensure every claim in the resume is accurate.")
    return {
        "overall_score": max(0, min(100, overall)),
        "label": "Strong match" if overall >= 80 else "Good match" if overall >= 65 else "Needs improvement",
        "factors": factors, "matched_keywords": matched, "missing_keywords": missing,
        "suggestions": suggestions, "word_count": word_count,
        "disclaimer": "This is a project-defined estimate, not an official score from an employer's ATS. Keyword presence does not prove skill proficiency."
    }
