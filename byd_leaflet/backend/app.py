"""Flask API for BYD Leaflet recommender."""
from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from fuel_savings import calculate_savings
from recommender import recommend

app = Flask(__name__)
CORS(app)

MODELS_JSON = Path(__file__).parent / "data" / "byd_models.json"


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/models", methods=["GET"])
def get_models():
    with open(MODELS_JSON) as f:
        models = json.load(f)
    return jsonify(models)


@app.route("/api/recommend", methods=["POST"])
def get_recommendation():
    answers = request.get_json(force=True)

    required = ["daily_km", "age_group", "drive_style", "long_trips", "home_charging"]
    missing = [k for k in required if k not in answers]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    result = recommend(answers)
    model = result["recommended"]
    fuel_type = answers.get("fuel_type", "petrol")

    daily_km_map = {"<20": 15, "20-50": 35, "50-100": 75, "100+": 150}
    daily_km = daily_km_map.get(answers["daily_km"], 35)

    savings = calculate_savings(daily_km, model, fuel_type)

    return jsonify({
        "powertrain": result["powertrain"],
        "recommended": model,
        "tagline": result["tagline"],
        "alternatives": result["alternatives"],
        "savings": savings,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5050)
