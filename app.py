"""HTTP inference demo using a versioned JSON model, never the legacy pickle."""
import json
import logging
import math
import os
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

FEATURES = ("CHAS", "RM", "TAX", "PTRATIO", "B", "LSTAT")
MODEL_PATH = Path(__file__).parent / "model_data" / "linear_model.json"
MAX_ROWS = 100


def load_model(path):
    """Fail at startup if the artifact is missing or incompatible."""
    model = json.loads(Path(path).read_text(encoding="utf-8"))
    if model.get("schema_version") != 1 or model.get("features") != list(FEATURES):
        raise ValueError("Unsupported model schema or feature order")
    values = model.get("coefficients", [])
    if len(values) != len(FEATURES):
        raise ValueError("Model must contain one coefficient per feature")
    if not all(
        isinstance(value, (int, float)) and not isinstance(value, bool)
        and math.isfinite(value)
        for value in [*values, model.get("intercept")]
    ):
        raise ValueError("Model coefficients must be finite numbers")
    return model


def parse_rows(payload):
    """Accept row-oriented JSON and the original course column-oriented format."""
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    if set(payload) == {"instances"}:
        rows = payload["instances"]
    elif set(payload) == set(FEATURES):
        columns = [payload[name] for name in FEATURES]
        if not all(isinstance(column, dict) for column in columns):
            raise ValueError("Legacy feature columns must be objects")
        keys = list(columns[0])
        if any(set(column) != set(keys) for column in columns):
            raise ValueError("All feature columns must have identical row keys")
        rows = [{name: payload[name][key] for name in FEATURES} for key in keys]
    else:
        raise ValueError("Supply instances or exactly these features: " + ", ".join(FEATURES))
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError(f"Supply between 1 and {MAX_ROWS} rows")
    validated = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(FEATURES):
            raise ValueError("Every row must contain exactly the documented features")
        values = [row[name] for name in FEATURES]
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) for value in values
        ):
            raise ValueError("Feature values must be finite JSON numbers")
        validated.append(values)
    return validated


def create_app(model_path=None):
    """Direct, WSGI, and test execution load the same model once."""
    model = load_model(model_path or MODEL_PATH)
    service = Flask(__name__)
    service.config["MAX_CONTENT_LENGTH"] = 64 * 1024

    @service.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @service.get("/")
    def home():
        return jsonify(service="Udacity housing inference demo", predict="/predict")

    @service.get("/health")
    def health():
        return jsonify(status="ok", model_version=model["schema_version"])

    @service.post("/predict")
    def predict():
        if not request.is_json:
            return jsonify(error="Content-Type must be application/json"), 415
        try:
            rows = parse_rows(request.get_json(silent=True))
            predictions = [
                model["intercept"] + math.fsum(
                    coefficient * value
                    for coefficient, value in zip(model["coefficients"], row)
                ) for row in rows
            ]
            if not all(math.isfinite(value) for value in predictions):
                raise ValueError("Feature values exceed the model's numerical range")
        except (ValueError, OverflowError) as error:
            return jsonify(error=str(error)), 400
        service.logger.info("Predicted %d row(s)", len(rows))
        return jsonify(prediction=predictions)

    return service


app = create_app()

if __name__ == "__main__":
    from waitress import serve

    logging.basicConfig(level=logging.INFO)
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
