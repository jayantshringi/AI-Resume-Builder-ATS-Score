from backend.ai_service import improve_bullet_points, generate_summary

def test_improve_bullet_points_empty():
    res = improve_bullet_points("")
    assert not res["success"]
    assert "no text" in res["message"].lower()

def test_generate_summary_structure():
    res = generate_summary("Python Developer", "Python, Flask, SQL", "Built web applications")
    assert "success" in res
    assert "result" in res

