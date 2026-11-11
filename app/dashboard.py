from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, render_template

dashboard_bp = Blueprint("dashboard", __name__)
REPORT_UNAVAILABLE_MESSAGE = (
    "Docker image measurements are not available yet. Build both Docker images "
    "and execute compare_images.ps1."
)


def _report_path() -> Path:
    configured_path = os.getenv("IMAGE_COMPARISON_REPORT")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / "reports" / "image-comparison.json"


def _positive_integer(report: dict[str, Any], key: str) -> int:
    value = report.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"Image comparison report has an invalid {key} value.")
    return value


def _valid_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def load_image_comparison() -> dict[str, Any]:
    with _report_path().open(encoding="utf-8-sig") as report_file:
        report = json.load(report_file)

    if not isinstance(report, dict):
        raise ValueError("Image comparison report must contain a JSON object.")

    baseline_image = report.get("baseline_image")
    optimized_image = report.get("optimized_image")
    generated_at = report.get("generated_at")
    measurement_method = report.get("measurement_method")
    if not all(
        isinstance(value, str) and value.strip()
        for value in (baseline_image, optimized_image, generated_at, measurement_method)
    ):
        raise ValueError("Image comparison report is missing required metadata.")
    if not _valid_timestamp(generated_at):
        raise ValueError("Image comparison report has an invalid generated_at timestamp.")

    baseline_bytes = _positive_integer(report, "baseline_size_bytes")
    optimized_bytes = _positive_integer(report, "optimized_size_bytes")
    saved_bytes = baseline_bytes - optimized_bytes

    return {
        "available": True,
        "baseline_image": baseline_image,
        "optimized_image": optimized_image,
        "baseline_size_bytes": baseline_bytes,
        "optimized_size_bytes": optimized_bytes,
        "baseline_size_mb": round(baseline_bytes / 1_000_000, 2),
        "baseline_size_mib": round(baseline_bytes / 1_048_576, 2),
        "optimized_size_mb": round(optimized_bytes / 1_000_000, 2),
        "optimized_size_mib": round(optimized_bytes / 1_048_576, 2),
        "saved_bytes": saved_bytes,
        "saved_mb": round(saved_bytes / 1_000_000, 2),
        "saved_mib": round(saved_bytes / 1_048_576, 2),
        "reduction_percent": round(saved_bytes / baseline_bytes * 100, 2),
        "generated_at": generated_at,
        "measurement_method": measurement_method,
    }


@dashboard_bp.get("/")
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.get("/api/optimization")
def optimization_metrics():
    try:
        return jsonify(load_image_comparison()), 200
    except FileNotFoundError:
        return jsonify(
            {"available": False, "message": REPORT_UNAVAILABLE_MESSAGE}
        ), 404
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return jsonify(
            {
                "available": False,
                "message": f"Docker image measurements could not be loaded: {exc}",
            }
        ), 503
