# Change report — 18 September 2026

Original HEAD: `7dfe8bd1167c85a32e0cec6f2f8091c441a703c6`.

## Implemented

- Replaced Python 3.7/sklearn 0.20 runtime dependencies with Python 3.12, Flask 3.1.3, Waitress and a versioned JSON model.
- Preserved the legacy pickle/dataset/output logs. The legacy pickle is never loaded. An offline NumPy training script creates a new, explicitly documented linear baseline; predictions are intentionally different from the old model.
- Fixed per-request scaling: the replacement model uses training-only scaling folded into fixed coefficients, so single-row and batch predictions agree.
- Added model validation at startup, a health endpoint, row/legacy-column input parsing, finite-number/schema validation, size/row limits and JSON errors.
- Added 20 meaningful API checks covering batch invariance, legacy compatibility, malformed inputs, numerical types, request limits and model-startup failure.
- Completed CircleCI test/lint execution; replaced the broken hadolint installation path with a simple Ruff/pytest Makefile workflow.
- Installed Git and OpenSSH explicitly before CircleCI checkout in the slim Python image, avoiding reliance on the native Git fallback.
- Added GitHub Actions validation with the same Python 3.12 Ruff/pytest commands and JUnit artifact upload, so checks do not depend on an external CircleCI integration being enabled.
- Updated Docker to a non-root Waitress service on port 8080; limited local binding to loopback in the run script. Repaired image tagging and required an explicit publish destination.
- Made Kubernetes execution declarative and rerunnable with rollout timeout and explicit image/namespace inputs.
- Rewrote README with current commands, contract, model provenance, actual local results and deployment limitations.

## Local verification

Python 3.12.14:

- 20 pytest cases passed.
- Ruff checks passed.
- Offline training completed: 404 training rows, 102 holdout rows, seed 42, holdout RMSE 4.588141041492039 in historical target units.
- Sample API response: prediction 30.679328738467255.
- git diff --check passed.
- The new GitHub Actions YAML passed checks for read-only permissions, Python 3.12, exact lint/test commands and the matching JUnit artifact path. CircleCI's checkout dependency order was also checked.

The training/test commands ran locally only. The Flask test client does not start an external service.

## Remaining limits

The Docker daemon was unavailable. Container build, registry publishing and Kubernetes execution were not run; remote CircleCI or GitHub Actions success is not claimed. The replacement baseline is an educational model using the historical course dataset, not a current valuation system. Numerical libraries can introduce insignificant retraining roundoff. Historical screenshots/output belong to the previous implementation.

No remote commit, push, archival or deployment was performed by this lane.
