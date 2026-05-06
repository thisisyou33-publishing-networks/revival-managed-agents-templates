---
name: data-explorer
description: >-
  General-purpose data profiling and exploration. Use when first encountering
  any dataset to understand its structure, quality, and analysis potential.
---

# Data explorer skill

Profile any tabular dataset (CSV, JSON, Parquet) and produce a structured
summary the other skills can consume.

## Workflow

1. **Scan workspace**: list all data files in the workspace directory.
2. **Load and profile each file**:
   - Row count, column count
   - Column names, data types, null counts, unique counts
   - Basic statistics (min, max, mean, median, std for numerics)
   - Value counts for categorical columns (top 10)
   - Correlation matrix for numeric columns
3. **Assess data quality**:
   - Missing value percentage per column
   - Potential data type issues (e.g., numbers stored as strings)
   - Duplicate row detection
   - Outlier detection (IQR method)
4. **Output a structured profile** as JSON for downstream skills.
5. **Recommend analysis directions** based on what you found.

## Output format

```json
{
  "files": [
    {
      "filename": "customers.csv",
      "rows": 91,
      "columns": 7,
      "schema": [
        {"name": "CustomerID", "dtype": "object", "nulls": 0, "unique": 91},
        {"name": "CompanyName", "dtype": "object", "nulls": 0, "unique": 91}
      ],
      "quality": {
        "missing_pct": {"Region": 0.60},
        "duplicates": 0
      },
      "recommendations": [
        "CustomerID is a unique string identifier",
        "Region column has a high missing percentage (60%)",
        "Can be joined with orders.csv on CustomerID to analyze customer behavior"
      ]
    }
  ]
}
```

## Key rules

- Never assume a specific dataset. Profile whatever is present.
- If no data files are found, inform the user and ask them to upload.
- Use `pandas` for profiling. It is pre-installed in the sandbox.
- Use `select_dtypes(include=["object", "str"])` for categorical columns.
- For large files (>100K rows), profile a sample first and note the sampling.
