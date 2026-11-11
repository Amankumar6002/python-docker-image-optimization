import json

from app.dashboard import REPORT_UNAVAILABLE_MESSAGE


def test_dashboard_renders_sections_without_notes_navigation(client):
    response = client.get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert 'id="overview"' in page
    assert 'id="comparison"' in page
    assert 'id="techniques"' in page
    assert 'id="architecture"' in page
    assert 'id="health"' in page
    assert 'id="about"' in page
    assert 'href="#notes"' not in page


def test_measurements_report_missing_shows_actionable_message(client, monkeypatch, tmp_path):
    monkeypatch.setenv(
        "IMAGE_COMPARISON_REPORT",
        str(tmp_path / "missing-image-comparison.json"),
    )

    response = client.get("/api/optimization")

    assert response.status_code == 404
    assert response.get_json() == {
        "available": False,
        "message": REPORT_UNAVAILABLE_MESSAGE,
    }


def test_measurements_are_calculated_from_report_bytes(client, monkeypatch, tmp_path):
    report_path = tmp_path / "image-comparison.json"
    report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-11-11T12:30:00+00:00",
                "measurement_method": "docker image inspect .Size",
                "baseline_image": "python-image-optimization:baseline",
                "optimized_image": "python-image-optimization:optimized",
                "baseline_size_bytes": 1_000_000_000,
                "optimized_size_bytes": 250_000_000,
                "saved_bytes": 1,
                "reduction_percent": 1,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("IMAGE_COMPARISON_REPORT", str(report_path))

    response = client.get("/api/optimization")
    metrics = response.get_json()

    assert response.status_code == 200
    assert metrics["available"] is True
    assert metrics["baseline_size_mb"] == 1000
    assert metrics["optimized_size_mb"] == 250
    assert metrics["saved_bytes"] == 750_000_000
    assert metrics["saved_mb"] == 750
    assert metrics["reduction_percent"] == 75


def test_malformed_measurements_report_is_reported_as_unavailable(
    client, monkeypatch, tmp_path
):
    report_path = tmp_path / "image-comparison.json"
    report_path.write_text("{invalid json", encoding="utf-8")
    monkeypatch.setenv("IMAGE_COMPARISON_REPORT", str(report_path))

    response = client.get("/api/optimization")

    assert response.status_code == 503
    assert response.get_json()["available"] is False
    assert "could not be loaded" in response.get_json()["message"]
