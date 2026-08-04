from __future__ import annotations

from agent.course import build_course_module


def test_course_module_builds_science_track():
    course = build_course_module("quiero una onda sinusoidal")

    assert course["mutation"] == "none"
    assert course["lane"] == "scientist_lab"
    assert course["input_mode"] == "creative"
    assert "Course" not in course["title"]
    assert len(course["lessons"]) == 3
    assert any("Simulation" in lesson["title"] for lesson in course["lessons"])
    assert "portfolio" in course["portfolio_artifact"].lower()


def test_course_module_builds_software_track():
    course = build_course_module("turn this README into an app with tests")

    assert course["lane"] == "software_builder"
    assert course["mutation"] == "none"
    assert any("Dry-run" in lesson["title"] or "Preview" in lesson["title"] for lesson in course["lessons"])
    assert "ready-for-review" in course["capstone_project"]
    assert any("kodex guide" in command for command in course["next_commands"])


def test_course_module_keeps_biomedical_request_safe():
    course = build_course_module("ver la piel como malla de Blender con vertices aristas y caras")

    assert course["lane"] == "scientist_lab"
    safety = " ".join(course["safety_boundary"]).lower()
    assert "educational" in safety
    assert "no provider calls" in safety
    assert "diagnose" in safety or "clinical" in safety or "medical" in safety


def test_course_module_assessment_is_stable():
    course = build_course_module("haz una portada BlackMamba premium")

    assert course["lane"] == "visual_artist"
    assert len(course["assessment"]) == 4
    assert all(isinstance(item, str) and item for item in course["assessment"])
    assert course["mutation"] == "none"
