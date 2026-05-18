# Document Processor Template

A template for building [Managed Agents using the Gemini API](TODO). This agent parses raw PDF invoices locally, runs automated matching and discrepancy audits against expense CSV logs, and outputs structured reconciliation reports and interactive presentation slideshows.

---

## 🚀 Features

*   **Offline PDF Parsing**: Extracts text from PDF invoices to local clean Markdown files completely offline.
*   **Data Reconciliation**: Automatically aligns invoices with expense reports and flags pricing, date, or merchant discrepancies.
*   **Vendor Verification**: Queries Wikidata and performs live search validation of merchants to check vendor legitimacy.
*   **Presentation Generation**: Designs interactive HTML slide presentation decks summarizing audit findings.

---

## 🛠️ Code Snippet Placeholder

```python
# TODO
```

---

## 🧪 Testing the Agent

To test the agent from the root of this repository:

```bash
cd document-processor
gemini-api agents test --prompt "Hello, what are your instructions?"
```
