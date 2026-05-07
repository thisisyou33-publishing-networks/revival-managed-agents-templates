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
import json
import yaml
import os
import sys

# This script defines the templates for Gemini Managed Agents.
# It outputs the templates as JSON, loading descriptions from agent.yaml files where applicable.

TEMPLATES = [
    {
        "id": "antigravity-preview",
        "name": "Antigravity Preview 05-2026",
        "description": "Our general-purpose autonomous agent running in a remote sandbox using the same harness that powers Antigravity. Customize its sources, tools, and instructions directly in the playground.",
        "chips": [
            "Explore your working environment",
            "Build a single page calculator using javascript and html",
            "Clone and explore python-genai repository from GitHub"
        ]
    },
    {
        "id": "ai-radio",
        "name": "AI Radio",
        "description": "",  # Loaded from agent.yaml
        "chips": [
            "Generate a 3-minute radio show called Daily Hacker Bites based on top Hacker News stories.",
            "Generate a 3-minute radio with a roundtable concept, educating listeners about https://github.com/google-deepmind/gemma",
            "Generate a 3-minute sports debate about the performance of the F1 McLaren Team in the most recent Grand Prix"
        ],
        "folder": "ai-radio"
    },
    {
        "id": "data-analyst",
        "name": "Data Analyst",
        "description": "",  # Loaded from agent.yaml
        "chips": [
            "Who is my biggest supplier and what happens if I lose them?",
            "How much revenue did I make this year?",
            "How can I reduce my costs?"
        ],
        "folder": "data-analyst"
    },
    {
        "id": "repo-maintainer",
        "name": "Open Source Maintainer",
        "description": "",  # Loaded from agent.yaml
        "chips": [
            "Find biggest issues with https://github.com/googleapis/python-genai and propose a fix",
            "Describe https://github.com/googleapis/python-genai repository",
            "What are the top customer issues with https://github.com/googleapis/python-genai repository"
        ],
        "folder": "repo-maintainer"
    },
    {
        "id": "document-processor",
        "name": "Document Processor",
        "description": "",  # Loaded from agent.yaml
        "chips": [
            "Turn my invoices into CSV",
            "Reconcile my invoices with Purchase Orders and flag discrepancies",
            "Verify legitimacy of my expenses by matching invoices with purchase orders and looking up vendors online"
        ],
        "folder": "document-processor"
    }
]

def load_descriptions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for template in TEMPLATES:
        if "folder" in template:
            yaml_path = os.path.join(base_dir, template["folder"], "agent.yaml")
            if os.path.exists(yaml_path):
                try:
                    with open(yaml_path, 'r') as f:
                        config = yaml.safe_load(f)
                        template["description"] = config.get("description", template["description"])
                except Exception as e:
                    print(f"Error reading {yaml_path}: {e}", file=sys.stderr)
            else:
                print(f"Warning: {yaml_path} not found.", file=sys.stderr)

def main():
    load_descriptions()
    print(json.dumps(TEMPLATES, indent=2))

if __name__ == "__main__":
    main()
