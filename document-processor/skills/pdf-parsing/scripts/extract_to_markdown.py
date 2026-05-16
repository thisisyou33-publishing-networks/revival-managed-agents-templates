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
"""Local-first PDF batch Markdown extraction utility. Runs 100% offline.

Usage:
    python3 extract_to_markdown.py --workspace .agents/workspace
"""

import argparse
import glob
import os
import shutil
import sys

try:
    import pypdf
except ImportError:
    pypdf = None


def extract_pypdf_text(pdf_path):
    """Extract raw text from PDF using pypdf locally."""
    if pypdf is None:
        print("Error: pypdf library is not installed. Please run 'pip install pypdf'.", file=sys.stderr)
        return ""
    try:
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


def prepare_invoices_directory(workspace):
    """Ensure all invoices live inside an isolated workspace/invoices/ folder."""
    invoices_dir = os.path.join(workspace, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    # Gather loose PDF files in root workspace and move them to invoices/
    loose_files = glob.glob(os.path.join(workspace, "*.pdf"))
    for f in loose_files:
        dest = os.path.join(invoices_dir, os.path.basename(f))
        shutil.move(f, dest)
        print(f"Moved loose invoice {os.path.basename(f)} to invoices/ directory.")

    return invoices_dir


def main():
    parser = argparse.ArgumentParser(description="Batch extract PDF invoices to markdown files locally")
    parser.add_argument("--workspace", default=".agents/workspace", help="Workspace directory")
    args = parser.parse_args()

    if not os.path.exists(args.workspace):
        print(f"Error: Workspace not found at {args.workspace}", file=sys.stderr)
        sys.exit(1)

    if pypdf is None:
        print("Error: pypdf library is not installed. Exiting.", file=sys.stderr)
        sys.exit(1)

    # 1. Isolate and prepare invoices/ subdirectory
    invoices_dir = prepare_invoices_directory(args.workspace)

    # Gather all isolated PDF invoices
    files = sorted(glob.glob(os.path.join(invoices_dir, "*.pdf")))
    if not files:
        print(f"No PDF invoice documents found in {invoices_dir}")
        sys.exit(0)

    print(f"Found {len(files)} isolated PDF invoice documents to process.")
    extracted_count = 0

    for f in files:
        base_name = os.path.splitext(os.path.basename(f))[0]
        output_md_path = os.path.join(invoices_dir, f"{base_name}.md")

        # Skip if markdown is already generated and up-to-date
        if os.path.exists(output_md_path):
            extracted_count += 1
            continue

        # Extract text locally using pypdf
        markdown_content = extract_pypdf_text(f)
        if markdown_content:
            with open(output_md_path, "w") as out_f:
                out_f.write(markdown_content)
            extracted_count += 1
            print(f"  [Local PDF] Extracted text from {os.path.basename(f)}")
        else:
            print(f"  ⚠️ Could not extract text for {os.path.basename(f)}")

    print(f"\n✅ Completed batch local extraction! {extracted_count}/{len(files)} files successfully exported to Markdown (.md) in {invoices_dir}")


if __name__ == "__main__":
    main()
