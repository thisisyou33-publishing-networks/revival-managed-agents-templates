---
name: northwind-data
description: Download and prepare the Northwind dataset (CSV files).
---

# Northwind Data

Download the Northwind dataset CSV files by cloning the sample repository. This dataset serves as the standard sample data for the Data Analyst Agent.

## Embedded Script

```bash
python skills/northwind-data/scripts/download_northwind.py --workspace ./workspace
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `workspace` | Root workspace directory |

### What it does

1. Clones `https://github.com/neo4j-contrib/northwind-neo4j.git` to a temporary directory.
2. Copies all `.csv` files from the `data/` folder in the repo to `{workspace}/data/`.
3. Cleans up the temporary directory.

### Output

Saves the following CSV files (and potentially others) to `{workspace}/data/`:
- `customers.csv`
- `orders.csv`
- `order-details.csv`
- `products.csv`
- `categories.csv`
- `suppliers.csv`
- `shippers.csv`
- `employees.csv`

## Usage in Workflow

Run this skill to bootstrap the workspace with realistic data before running analyses or answering user questions if the workspace is empty.
