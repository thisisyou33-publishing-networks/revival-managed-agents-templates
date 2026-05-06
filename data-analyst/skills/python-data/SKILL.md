---
name: python-data
description: Performs heavy numerical compute and statistical analysis inside the sandbox.
---

# Python data skill

Run complex calculations, regressions, and aggregations using pandas and
scikit-learn in the sandbox.

## Workflow

1. **Write a Python script** using `pandas`, `numpy`, or `sklearn` to:
   - Join, filter, and aggregate tables.
   - Compute statistics (mean, median, stddev, correlations).
   - Build or evaluate ML models.
   - Run statistical tests (chi-square, t-test) when appropriate.
2. **Execute in the sandbox.** Run via `python3 script.py`.
3. **Handle errors.** If the code fails, read the traceback and fix it.
4. **Return structured output.** Print results as JSON for downstream skills.

## Example output

```json
[
  {"segment": "High Risk", "churn_rate": 0.34, "avg_tenure": 2.1},
  {"segment": "Low Risk",  "churn_rate": 0.05, "avg_tenure": 14.7}
]
```

## Notes

- Use `select_dtypes(include=["object", "str"])` for categorical columns
  (avoids the pandas 4 deprecation warning).
- Install missing packages with `pip install -q <package>` before importing.
