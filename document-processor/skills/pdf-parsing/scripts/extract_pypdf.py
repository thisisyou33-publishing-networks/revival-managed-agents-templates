#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Local text extraction utility using pypdf.

Usage:
    python3 extract_pypdf.py --file ./workspace/invoices/invoice.pdf
"""

import argparse
import os
import sys


def extract_pypdf(pdf_path):
    """Locally extract text from PDF using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error: pypdf extraction failed for {os.path.basename(pdf_path)}: {e}", file=sys.stderr)
        return ""


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF locally using pypdf")
    parser.add_argument("--file", required=True, help="Path to the PDF file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found at {args.file}", file=sys.stderr)
        sys.exit(1)

    if not args.file.lower().endswith(".pdf"):
        print("Error: Local extract_pypdf only supports .pdf files", file=sys.stderr)
        sys.exit(1)

    text = extract_pypdf(args.file)
    if not text:
        sys.exit(1)

    # Print the raw extracted text to stdout
    print(text)


if __name__ == "__main__":
    main()
