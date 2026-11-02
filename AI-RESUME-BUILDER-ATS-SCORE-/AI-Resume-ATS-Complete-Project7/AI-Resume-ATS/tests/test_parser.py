from backend.resume_parser import extract_resume_text

def test_text_parser(tmp_path):
    file_path = tmp_path / "resume.txt"
    file_path.write_text("Sample resume text", encoding="utf-8")
    assert extract_resume_text(str(file_path)) == "Sample resume text"
