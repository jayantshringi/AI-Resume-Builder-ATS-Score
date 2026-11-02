from backend.ats_engine import analyze_resume

def test_score_is_within_range():
    result = analyze_resume(
        "Mohit Kumar\nmohit@example.com\n9876543210\nSkills\nPython SQL HTML CSS\nEducation\nBCA 2024\nProjects\nBuilt a Flask project in 2025.",
        "Python developer needed. Required skills: Python, SQL, HTML, CSS, Flask.",
        "Python Developer"
    )
    assert 0 <= result["overall_score"] <= 100
    assert result["matched_keywords"]

def test_different_resume_changes_results():
    job = "Python developer with Python, SQL and Flask skills."
    strong = analyze_resume("Python developer\nEmail: a@b.com\nPhone: 1234567890\nSkills\nPython SQL Flask\nEducation BCA 2024\nProjects developed app", job, "Python Developer")
    weak = analyze_resume("My name is Sam. I like music and travel.", job, "Python Developer")
    assert strong["overall_score"] != weak["overall_score"]
    assert len(weak["missing_keywords"]) >= len(strong["missing_keywords"])

def test_expanded_skills_and_degrees():
    job = "DevOps Engineer with Docker, Kubernetes, Terraform and CI/CD."
    resume = "Candidate Name\nEmail: test@example.com\nPhone: +1 555-234-5678\nSkills: Docker, Kubernetes, Terraform, CI/CD, Linux\nEducation: B.S. in Computer Science (2022)\nExperience: Automated deployment pipelines."
    result = analyze_resume(resume, job, "DevOps Engineer")
    assert "docker" in result["matched_keywords"]
    assert "kubernetes" in result["matched_keywords"]
    # Education should be detected from "B.S."
    edu_factor = next(f for f in result["factors"] if f["name"] == "Education and experience")
    assert edu_factor["score"] >= 50
