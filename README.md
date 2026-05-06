# Gemini Managed Agents Templates

> [!CAUTION]
> **Disclaimer**: This is not a supported Google product.

This repository contains a collection of templates for building and deploying Gemini Managed Agents using the Gemini API. These templates demonstrate the power of the Gemini API sandbox, including code execution, filesystem operations, and web search.

## Available Templates

- **Data Analyst**: Upload a CSV and get full data analysis with charts and insights.
- **AI Radio**: Turn today's top Hacker News stories into a radio program (podcast briefing).
- **Repo Maintainer**: Provide a GitHub repo URL, find top issues, fix them, and send Pull Requests.
- **Document Processor**: A template for processing and analyzing documents.

## Getting Started

To use these templates, you can reference them in your Gemini API calls or use the Gemini API CLI to scaffold new agents based on these templates.

## Running Probers

Each template directory contains a `probers.sh` script that can be used to test the agent template by sending a "Hello" prompt to the Gemini API. These probers read the template information (like `AGENTS.md` and skills) dynamically from disk.

To run a prober:

1.  Set your `GEMINI_API_KEY` environment variable:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```

2.  Navigate to the template directory you want to test (e.g., `data-analyst`):
    ```bash
    cd data-analyst
    ```

3.  Run the prober script:
    ```bash
    ./probers.sh
    ```

The script will call `../generate_payload.py` to construct the payload dynamically and then use `curl` to make the API request.


## Disclaimer

**This is not an official Google product.** It is maintained by the community and Google engineers as an open-source project under the Apache 2.0 License.
