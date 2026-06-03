"""
Lightweight ML recommender trained on BYD survey data.
Predicts powertrain type (BEV/PHEV), then ranks models by fit.
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score

# Allow importing survey_utils from parent project
PARENT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PARENT))

DATA_DIR = Path(__file__).parent / "data"
MODEL_PATH = Path(__file__).parent / "model.pkl"
MODELS_JSON = DATA_DIR / "byd_models.json"

# ── Feature engineering from survey columns ───────────────────────────────────

DD_BUCKET = {
    "Less than 10 km": 5,
    "10 – 20 km": 15,
    "21 – 50 km": 35,
    "51 – 100 km": 75,
    "More than 100 km": 150,
}

AGE_BUCKET = {
    "18–24": 0,
    "25–34": 1,
    "35–44": 2,
    "45–54": 3,
    "55+": 4,
}


def _powertrain_label(val: str) -> str | None:
    """Map raw survey powertrain string to BEV or PHEV."""
    if pd.isna(val):
        return None
    v = str(val).upper()
    if "BEV" in v:
        return "BEV"
    if "PHEV" in v or "REEV" in v or "DM" in v:
        return "PHEV"
    return None


def _charging_score(val: str) -> int:
    if pd.isna(val):
        return 0
    v = str(val).lower()
    if "very" in v or "extremely" in v or "5" in v:
        return 2
    if "convenient" in v or "4" in v or "3" in v:
        return 1
    return 0


def build_training_data() -> tuple[np.ndarray, np.ndarray]:
    # Synthetic data is the authoritative training source.
    # Survey data cannot be used directly because daily_driving_distance,
    # drive_style, and long_trips are all collinear in survey responses
    # (all derived from the same distance question), so a tree trained on
    # survey data ignores the independent quiz signals at inference time.
    return _synthetic_data()


def _synthetic_data() -> tuple[np.ndarray, np.ndarray]:
    """Rule-based synthetic training set matching quiz feature space.

    Features (must match _quiz_to_features order):
      [daily_km, age, drive_style, long_trips, charging]

    All five features are treated as INDEPENDENT signals — the same way
    a quiz user answers them — so the learned tree uses all of them.
    """
    rng = np.random.default_rng(42)
    X, y = [], []

    # ── BEV profiles ──────────────────────────────────────────────────────
    # Short city commute, home charging, no long trips (core BEV buyer)
    for _ in range(100):
        X.append([rng.choice([5, 15, 35]), rng.choice([0, 1, 2]),
                  0, 0, rng.choice([1, 2])])
        y.append("BEV")

    # Medium mixed commute, has charging, occasional long trip covered by range
    for _ in range(80):
        X.append([rng.choice([35, 75]), rng.integers(0, 4),
                  1, 0, rng.choice([1, 2])])
        y.append("BEV")

    # BEV on long trips too (they charge en-route) — high daily_km + charging
    for _ in range(40):
        X.append([rng.choice([75, 150]), rng.integers(0, 3),
                  rng.choice([1, 2]), 1, 2])
        y.append("BEV")

    # Young urban, any charging situation, no long trips
    for _ in range(30):
        X.append([rng.choice([5, 15]), 0, 0, 0, rng.integers(0, 3)])
        y.append("BEV")

    # ── PHEV profiles ─────────────────────────────────────────────────────
    # Long distance highway driver, no home charging (range anxiety)
    for _ in range(100):
        X.append([rng.choice([75, 150]), rng.integers(1, 5),
                  2, 1, 0])
        y.append("PHEV")

    # Frequent long trips + no reliable charging → needs fuel backup
    for _ in range(70):
        X.append([rng.choice([35, 75, 150]), rng.integers(1, 5),
                  rng.choice([1, 2]), 1, rng.choice([0, 1])])
        y.append("PHEV")

    # High daily km, no home charging, any age
    for _ in range(50):
        X.append([rng.choice([75, 150]), rng.integers(0, 5),
                  rng.choice([1, 2]), rng.choice([0, 1]), 0])
        y.append("PHEV")

    return np.array(X, dtype=float), np.array(y)


def train_and_save() -> DecisionTreeClassifier:
    X, y = build_training_data()
    clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=42)
    scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
    print(f"[recommender] CV accuracy: {scores.mean():.2f} ± {scores.std():.2f}")
    clf.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    print(f"[recommender] Model saved → {MODEL_PATH}")
    return clf


def load_model() -> DecisionTreeClassifier:
    if not MODEL_PATH.exists():
        print("[recommender] No model.pkl found — training now...")
        return train_and_save()
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def _quiz_to_features(answers: dict) -> list[float]:
    """Convert quiz answers dict to feature vector."""
    daily_km_map = {"<20": 10, "20-50": 35, "50-100": 75, "100+": 150}
    age_map = {"18-24": 0, "25-34": 1, "35-44": 2, "35-54": 2, "45-54": 3, "55+": 4}
    style_map = {"city": 0, "mixed": 1, "highway": 2}

    daily_km = daily_km_map.get(answers.get("daily_km", "20-50"), 35)
    age = age_map.get(answers.get("age_group", "25-34"), 1)
    drive_style = style_map.get(answers.get("drive_style", "mixed"), 1)
    long_trips = 1 if answers.get("long_trips", False) else 0
    charging = 2 if answers.get("home_charging") == "yes" else (1 if answers.get("home_charging") == "unsure" else 0)

    return [daily_km, age, drive_style, long_trips, charging]


def _score_model(model: dict, answers: dict, powertrain: str) -> float:
    """Score a car model against user answers (0–1)."""
    score = 0.0

    daily_km_map = {"<20": 10, "20-50": 35, "50-100": 75, "100+": 150}
    daily_km = daily_km_map.get(answers.get("daily_km", "20-50"), 35)

    # Powertrain match is critical
    if model["type"] == powertrain:
        score += 0.5

    # Range fit
    model_range = model.get("ev_range_km", model["range_km"]) if model["type"] == "PHEV" else model["range_km"]
    if model_range >= daily_km * 1.5:
        score += 0.2
    elif model_range >= daily_km:
        score += 0.1

    # Lifestyle tags
    if answers.get("long_trips") and "long_trips" in model["best_for"]:
        score += 0.1
    if answers.get("home_charging") == "no" and "no_home_charging" in model["best_for"]:
        score += 0.1
    if answers.get("drive_style") in model["best_for"]:
        score += 0.1

    # Age / segment
    age_group = answers.get("age_group", "25-34")
    if age_group in ("18-24", "25-34") and "young_driver" in model["best_for"]:
        score += 0.05
    if age_group in ("35-44", "35-54", "45-54") and "family" in model["best_for"]:
        score += 0.05

    return score


def _pick_tagline(model: dict, answers: dict) -> dict:
    taglines = model.get("taglines", {})
    age = answers.get("age_group", "25-34")
    style = answers.get("drive_style", "city")
    long_trips = answers.get("long_trips", False)

    if long_trips and "long_trips" in taglines:
        return taglines["long_trips"]
    if long_trips and "highway" in taglines:
        return taglines["highway"]
    if age in ("18-24", "25-34") and "young" in taglines:
        return taglines["young"]
    if style in taglines:
        return taglines[style]
    if "family" in taglines and answers.get("age_group") in ("35-44", "35-54", "45-54"):
        return taglines["family"]
    return taglines.get("default", {"en": "Discover your perfect drive.", "th": "ค้นพบการขับขี่ที่ใช่สำหรับคุณ"})


def recommend(answers: dict) -> dict:
    clf = load_model()
    features = _quiz_to_features(answers)
    powertrain = clf.predict([features])[0]

    with open(MODELS_JSON) as f:
        all_models = json.load(f)

    scored = [(m, _score_model(m, answers, powertrain)) for m in all_models]
    scored.sort(key=lambda x: x[1], reverse=True)

    top = scored[0][0]
    alternatives = [m for m, _ in scored[1:3] if m["type"] == powertrain]

    return {
        "powertrain": powertrain,
        "recommended": top,
        "tagline": _pick_tagline(top, answers),
        "alternatives": alternatives[:2],
    }


if __name__ == "__main__":
    train_and_save()
