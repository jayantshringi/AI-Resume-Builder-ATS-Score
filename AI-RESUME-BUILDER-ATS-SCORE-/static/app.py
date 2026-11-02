from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from pypdf import PdfReader
from PIL import Image
from io import BytesIO
import pytesseract
import re
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

# General resume vocabulary for general ATS-readiness.
SKILLS = {
    "python","java","javascript","typescript","html","css","react","angular","vue",
    "node","node.js","express","flask","django","php","c","c++","c#","ruby","go",
    "sql","mysql","postgresql","mongodb","oracle","database","aws","azure","gcp",
    "docker","kubernetes","jenkins","linux","git","github","gitlab","rest api","api",
    "microservices","machine learning","deep learning","artificial intelligence",
    "data analysis","data science","pandas","numpy","tensorflow","pytorch","power bi",
    "tableau","excel","testing","debugging","agile","scrum","communication",
    "leadership","teamwork","problem solving","project management","collaboration",
    "management","development","design","analysis","research","strategy","optimization",
    "implementation","customer service","sales","marketing","finance","accounting",
    "figma","photoshop","canva","seo","content marketing","social media"
}

SECTIONS = {
    "Summary": ["summary","professional summary","profile","objective"],
    "Experience": ["experience","work experience","professional experience","employment"],
    "Education": ["education","academic background","qualifications"],
    "Skills": ["skills","technical skills","core skills","key skills"],
    "Projects": ["projects","academic projects","personal projects"],
    "Certifications": ["certifications","certificates","licenses"],
    "Achievements": ["achievements","accomplishments","awards"]
}

ACTION_WORDS = {
    "developed","created","built","designed","implemented","managed","led","improved",
    "increased","reduced","optimized","analyzed","achieved","delivered","launched",
    "automated","maintained","engineered","coordinated","organized","solved","tested",
    "deployed","generated","negotiated","streamlined","mentored","executed"
}

TEMPLATE_CATALOG = [
    {"id": 1, "name": "Modern Blue", "style": "modern", "color": "#2563eb"},
    {"id": 2, "name": "Executive Navy", "style": "executive", "color": "#0f3d67"},
    {"id": 3, "name": "Minimal Gray", "style": "minimal", "color": "#475569"},
    {"id": 4, "name": "Creative Purple", "style": "creative", "color": "#7c3aed"},
    {"id": 5, "name": "Elegant Teal", "style": "elegant", "color": "#0f766e"},
    {"id": 6, "name": "Professional Green", "style": "professional", "color": "#15803d"},
    {"id": 7, "name": "Classic Black", "style": "classic", "color": "#111827"},
    {"id": 8, "name": "Tech Cyan", "style": "tech", "color": "#0891b2"},
    {"id": 9, "name": "Corporate Indigo", "style": "corporate", "color": "#4338ca"},
    {"id": 10, "name": "Clean Rose", "style": "clean", "color": "#be123c"},
    {"id": 11, "name": "Fresh Orange", "style": "fresh", "color": "#ea580c"},
    {"id": 12, "name": "Soft Violet", "style": "soft", "color": "#8b5cf6"},
    {"id": 13, "name": "Bold Red", "style": "bold", "color": "#dc2626"},
    {"id": 14, "name": "Ocean", "style": "ocean", "color": "#0369a1"},
    {"id": 15, "name": "Forest", "style": "forest", "color": "#166534"},
    {"id": 16, "name": "Slate", "style": "slate", "color": "#334155"},
    {"id": 17, "name": "Royal", "style": "royal", "color": "#5b21b6"},
    {"id": 18, "name": "Mint", "style": "mint", "color": "#047857"},
    {"id": 19, "name": "Amber", "style": "amber", "color": "#b45309"},
    {"id": 20, "name": "Sky", "style": "sky", "color": "#0284c7"},
    {"id": 21, "name": "Plum", "style": "plum", "color": "#86198f"},
    {"id": 22, "name": "Graphite", "style": "graphite", "color": "#374151"},
    {"id": 23, "name": "Aqua", "style": "aqua", "color": "#0d9488"},
    {"id": 24, "name": "Midnight", "style": "midnight", "color": "#1e3a8a"}
]

DEFAULT_RESUME = {
    "name": "",
    "role": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": "",
    "website": "",
    "summary": "",
    "skills": "",
    "experience": "",
    "education": "",
    "projects": "",
    "certifications": "",
    "achievements": "",
    "template": 1,
    "color": "#2563eb"
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def contains_term(text, term):
    return bool(re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", text))

def extract_pdf_text(file):
    try:
        file.stream.seek(0)
        reader = PdfReader(file.stream)
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception:
        return ""

def extract_image_text(file):
    try:
        file.stream.seek(0)
        image = Image.open(BytesIO(file.stream.read()))
        return pytesseract.image_to_string(image)
    except Exception:
        return ""

def extract_resume_text(file):
    name = file.filename.lower()
    if name.endswith(".pdf"):
        return extract_pdf_text(file)
    if name.endswith((".jpg", ".jpeg", ".png")):
        return extract_image_text(file)
    return ""

def keyword_score(text):
    found = sorted([s for s in SKILLS if contains_term(text, s)])
    return min(100, round(len(found) / 14 * 100)), found

def structure_score(text):
    found = []
    for section, aliases in SECTIONS.items():
        if any(alias in text for alias in aliases):
            found.append(section)
    return round(len(found) / len(SECTIONS) * 100), found

def contact_score(text):
    email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))
    phone = bool(re.search(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)", text))
    linkedin = "linkedin" in text
    github = "github" in text
    score = (35 if email else 0) + (35 if phone else 0) + (15 if linkedin else 0) + (15 if github else 0)
    return score, email, phone, linkedin, github

def experience_score(text):
    years = len(re.findall(r"\b(?:19|20)\d{2}\b", text))
    roles = sum(1 for word in [
        "intern","internship","engineer","developer","manager","analyst","designer",
        "consultant","specialist","coordinator","assistant","director","lead","executive"
    ] if word in text)
    score = years * 8 + roles * 10 + (20 if "experience" in text else 0)
    return min(100, score), years

def education_score(text):
    terms = [
        "bachelor","master","b.tech","m.tech","b.e","m.e","bsc","msc","mba",
        "phd","degree","diploma","university","college","school"
    ]
    found = sum(1 for t in terms if t in text)
    return min(100, found * 18 + (45 if "education" in text else 0))

def achievement_score(text):
    actions = sorted([a for a in ACTION_WORDS if contains_term(text, a)])
    numbers = len(re.findall(r"\b\d+(?:\.\d+)?\s*(?:%|percent|k|m|million|thousand)?\b", text))
    return min(100, len(actions) * 5 + min(numbers, 10) * 6), actions, numbers

def length_score(words):
    if words < 80: return 20
    if words < 150: return 50
    if words < 300: return 70
    if words <= 900: return 100
    if words <= 1200: return 85
    return 65

def consistency_score(text, sections):
    score = 40
    if len(sections) >= 4: score += 25
    if len(re.findall(r"\b(?:19|20)\d{2}\b", text)) >= 2: score += 15
    if text.count("•") + text.count("·") + text.count("- ") >= 3: score += 20
    return min(100, score)

def readability_score(text, filename, words):
    score = 60
    if len(text) > 100: score += 15
    if any(x in text for x in ["summary","experience","education","skills"]): score += 15
    if words >= 150: score += 10
    if filename.lower().endswith(".pdf"): score += 5
    return min(100, score)

def calculate_ats(raw_text, filename):
    text = normalize(raw_text)
    words = len(text.split())

    keywords, skills_found = keyword_score(text)
    structure, sections = structure_score(text)
    contact, email, phone, linkedin, github = contact_score(text)
    experience, years = experience_score(text)
    education = education_score(text)
    achievements, actions, numbers = achievement_score(text)
    length = length_score(words)
    consistency = consistency_score(text, sections)
    formatting = readability_score(text, filename, words)
    skills = min(100, round(len(skills_found) / 10 * 100))

    score = round(
        keywords * .18 +
        skills * .10 +
        structure * .12 +
        experience * .12 +
        education * .08 +
        contact * .08 +
        achievements * .10 +
        formatting * .08 +
        length * .06 +
        consistency * .08
    )

    result = {
        "score": max(0, min(100, score)),
        "keywords": keywords,
        "skills": skills,
        "structure": structure,
        "experience": experience,
        "education": education,
        "contact": contact,
        "achievements": achievements,
        "formatting": formatting,
        "length": length,
        "consistency": consistency,
        "skills_found": skills_found,
        "sections": sections,
        "actions": actions,
        "word_count": words,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "year_count": years,
        "number_count": numbers
    }

    # Personalized tips, ordered by the weakest metrics.
    metrics = [
        ("keywords", "Improve keywords", "Use accurate, standard terminology that describes your real experience and skills."),
        ("skills", "Add stronger skills", "Add relevant technical and professional skills that you genuinely possess."),
        ("experience", "Strengthen experience", "Add roles, dates, responsibilities, tools used and measurable results."),
        ("education", "Complete education", "Clearly show your degree, institution, field and graduation information."),
        ("structure", "Improve structure", "Use clear ATS-friendly headings such as Summary, Experience, Skills and Education."),
        ("achievements", "Add measurable achievements", "Use action verbs and numbers such as %, revenue, time saved or team size."),
        ("contact", "Complete contact details", "Make your email and phone easy to find; add LinkedIn if appropriate."),
        ("formatting", "Improve ATS readability", "Prefer clean text, simple headings and a readable one-column structure."),
        ("length", "Adjust resume length", "Keep enough useful detail without adding large amounts of irrelevant content."),
        ("consistency", "Improve consistency", "Keep dates, headings, bullets and formatting patterns consistent.")
    ]
    tips = []
    for key, title, detail in sorted(metrics, key=lambda x: result[x[0]])[:5]:
        if result[key] < 85:
            tips.append({"title": title, "detail": detail, "score": result[key]})
    result["tips"] = tips

    return result

def get_resume():
    return session.get("resume", DEFAULT_RESUME.copy())

@app.context_processor
def inject_globals():
    return {"template_catalog": TEMPLATE_CATALOG}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["logged_in"] = True
        session["user"] = request.form.get("email", "User")
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session["logged_in"] = True
        session["user"] = request.form.get("email", "User")
        flash("Account created successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", resume=get_resume())

@app.route("/builder", methods=["GET", "POST"])
def builder():
    resume = get_resume()
    if request.method == "POST":
        for key in DEFAULT_RESUME:
            if key in request.form:
                resume[key] = request.form.get(key, "").strip()
        resume["template"] = int(request.form.get("template", resume.get("template", 1)))
        resume["color"] = request.form.get("color", resume.get("color", "#2563eb"))
        session["resume"] = resume
        flash("Resume saved successfully.", "success")
        return redirect(url_for("preview"))
    return render_template("builder.html", resume=resume)

@app.route("/preview")
def preview():
    return render_template("preview.html", resume=get_resume())

@app.route("/templates")
def templates():
    selected = request.args.get("selected", type=int) or get_resume().get("template", 1)
    return render_template("templates.html", selected=selected)

@app.route("/template-detail/<int:template_id>")
def template_detail(template_id):
    template = next((t for t in TEMPLATE_CATALOG if t["id"] == template_id), TEMPLATE_CATALOG[0])
    return render_template("template-detail.html", template=template)

@app.route("/select-template/<int:template_id>", methods=["POST", "GET"])
def select_template(template_id):
    if 1 <= template_id <= len(TEMPLATE_CATALOG):
        resume = get_resume()
        resume["template"] = template_id
        resume["color"] = next(t["color"] for t in TEMPLATE_CATALOG if t["id"] == template_id)
        session["resume"] = resume
    return redirect(url_for("builder"))

@app.route("/ats")
def ats():
    return render_template("ats.html")

@app.route("/ats-result", methods=["GET", "POST"])
def ats_result():
    if request.method == "GET":
        return redirect(url_for("ats"))

    file = request.files.get("resume")
    if not file or not file.filename:
        return render_template("error.html", message="Please select a resume before checking the ATS score."), 400

    if not allowed_file(file.filename):
        return render_template("error.html", message="Only PDF, JPG, JPEG and PNG files are supported."), 400

    filename = secure_filename(file.filename)
    text = extract_resume_text(file)

    if len(text.strip()) < 30:
        return render_template(
            "error.html",
            message="The resume could not be read. Use a text-based PDF or a clear JPG/PNG image."
        ), 400

    result = calculate_ats(text, filename)
    session["last_ats"] = result

    return render_template("ats-result.html", result=result, filename=filename)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks! Your message has been received.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
