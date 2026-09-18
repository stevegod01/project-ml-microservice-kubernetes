"""Reproduce a linear baseline from the checked-in historical course dataset."""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
DATA = ROOT / "model_data" / "housing.csv"
FEATURES = ["CHAS", "RM", "TAX", "PTRATIO", "B", "LSTAT"]
INDICES = [3, 5, 9, 10, 11, 12]


def train():
    data = np.loadtxt(DATA)
    order = np.random.default_rng(42).permutation(len(data))
    split = int(len(data) * 0.8)
    training, holdout = order[:split], order[split:]
    features, target = data[:, INDICES], data[:, 13]
    mean, scale = features[training].mean(axis=0), features[training].std(axis=0)
    design = np.column_stack([np.ones(split), (features[training] - mean) / scale])
    fitted, _, _, _ = np.linalg.lstsq(design, target[training], rcond=None)
    coefficients = fitted[1:] / scale
    intercept = fitted[0] - coefficients @ mean
    predicted = features[holdout] @ coefficients + intercept
    result = {
        "schema_version": 1, "features": FEATURES,
        "coefficients": coefficients.tolist(), "intercept": float(intercept),
        "training": {
            "method": "ordinary least squares; scaling fitted only on training rows",
            "seed": 42, "training_rows": len(training), "holdout_rows": len(holdout),
            "holdout_rmse": float(np.sqrt(np.mean((predicted - target[holdout]) ** 2))),
            "target_unit": "historical median home value in thousands of USD",
            "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
            "numpy_version": np.__version__,
        },
    }
    (ROOT / "model_data" / "linear_model.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["training"], indent=2))


if __name__ == "__main__":
    train()
