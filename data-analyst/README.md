# Data Analyst Template

A template for building [Managed Agents using the Gemini API](https://ai.google.dev/gemini-api/managed-agents). This agent profiles database schemas, computes statistics, and trains machine learning models on a pre-bootstrapped dataset using Pandas and Scikit-Learn.

---

## 🚀 Features

*   **Pre-Bootstrapped Dataset**: Access to cleaned Northwind database CSV files for orders, suppliers, products, and more.
*   **Dataset Analysis**: Uses the data-explorer skills to analyze table schemas, null counts, and data quality.
*   **Predictive Modeling**: Runs custom Python modeling scripts for regression or classification (such as forecasting sales and detecting anomalies) on-demand.
*   **Proactive Momentum**: Automatically offers 2-3 specific contextual follow-up questions to deepen analytical insights.

---

## 🛠️ Code Snippet Placeholder

```bash
# TODO
cd data-analyst
gemini-api agents test --prompt "Who is my biggest customer?"
```

---

## 🧪 Testing the Prober

To quickly test the template end-to-end, run:

```bash
export GEMINI_API_KEY="your_api_key_here"
./probers.sh
```
