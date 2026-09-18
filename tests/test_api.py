"""API contract and numerical regression checks; no external network or cloud."""
import json
import math

import pytest

from app import MODEL_PATH, create_app

ROW = {"CHAS": 0, "RM": 6.575, "TAX": 296, "PTRATIO": 15.3, "B": 396.9, "LSTAT": 4.98}


@pytest.fixture()
def client():
    service = create_app()
    service.config["TESTING"] = True
    return service.test_client()


def test_health_checks_loaded_model(client):
    assert client.get("/health").json == {"status": "ok", "model_version": 1}


def test_prediction_matches_artifact_and_does_not_depend_on_batch(client):
    alone = client.post("/predict", json={"instances": [ROW]})
    other = {**ROW, "RM": 4.0, "LSTAT": 24.0}
    batch = client.post("/predict", json={"instances": [ROW, other]})
    model = json.loads(MODEL_PATH.read_text())
    expected = model["intercept"] + math.fsum(
        coefficient * ROW[name]
        for coefficient, name in zip(model["coefficients"], model["features"])
    )
    assert alone.status_code == 200
    assert alone.json["prediction"] == pytest.approx([expected])
    assert batch.json["prediction"][0] == alone.json["prediction"][0]
    assert batch.json["prediction"][0] != batch.json["prediction"][1]


def test_legacy_column_format_remains_supported(client):
    legacy = {name: {"0": value} for name, value in ROW.items()}
    assert client.post("/predict", json=legacy).json == client.post(
        "/predict", json={"instances": [ROW]}
    ).json


@pytest.mark.parametrize("payload", [
    None, [], {}, {"instances": []}, {"instances": [ROW] * 101},
    {"instances": [{**ROW, "extra": 1}]}, {"instances": [{"RM": 6.5}]},
    {"instances": [{**ROW, "RM": "6.5"}]}, {"instances": [{**ROW, "RM": True}]},
    {"instances": [{**ROW, "RM": float("inf")}]},
    {"instances": [{**ROW, "RM": float("nan")}]},
    {name: {"0" if name == "RM" else "1": value} for name, value in ROW.items()},
])
def test_invalid_input_is_actionable_400(client, payload):
    result = client.post("/predict", data=json.dumps(payload), content_type="application/json")
    assert result.status_code == 400
    assert result.json["error"]


def test_malformed_json_is_400(client):
    assert client.post("/predict", data="{", content_type="application/json").status_code == 400


def test_content_type_is_required(client):
    assert client.post("/predict", data="text").status_code == 415


def test_request_size_is_bounded(client):
    result = client.post("/predict", data="x" * 70000, content_type="application/json")
    assert result.status_code == 413
    assert result.json["error"]


def test_missing_model_fails_at_startup(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_app(tmp_path / "missing.json")


def test_invalid_model_fails_at_startup(tmp_path):
    artifact = tmp_path / "model.json"
    artifact.write_text('{"schema_version": 1, "features": []}')
    with pytest.raises(ValueError, match="schema"):
        create_app(artifact)
