#!/usr/bin/env python3
import os
import json
import yaml
import base64
import sys

def make_payload():
    if not os.path.exists('agent.yaml'):
        print("Error: agent.yaml not found in current directory.", file=sys.stderr)
        sys.exit(1)
        
    with open('agent.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    agent_id = config.get('id')
    base_agent = config.get('base_agent', 'waverunner')
    tools = config.get('tools', [])
    instructions = config.get('instructions')
    
    sources = []
    
    # Special credentials source
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
        
    sources.append({
        "type": "inline",
        "target": "/credentials/.env",
        "content": f"GEMINI_API_KEY={api_key}\n"
    })
    
    # Read AGENTS.md
    if os.path.exists('AGENTS.md'):
        with open('AGENTS.md', 'r') as f:
            content = f.read()
        sources.append({
            "type": "inline",
            "target": "/.agents/AGENTS.md",
            "content": content
        })
        
    # Helper function to add files
    def add_files(dir_path):
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    target_path = "/.agents/" + full_path
                    
                    # Check if binary or text
                    # Simple heuristic: check extension
                    if file.endswith(('.py', '.md', '.txt', '.sh', '.csv', '.env', '.gitignore', '.yaml')):
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            sources.append({
                                "type": "inline",
                                "target": target_path,
                                "content": content
                            })
                        except UnicodeDecodeError:
                            # Fallback to base64 if utf-8 decode fails
                            with open(full_path, 'rb') as f:
                                content = base64.b64encode(f.read()).decode('utf-8')
                            sources.append({
                                "type": "inline",
                                "target": target_path,
                                "content": content,
                                "encoding": "base64"
                            })
                    else:
                        # Assume binary, base64 encode
                        with open(full_path, 'rb') as f:
                            content = base64.b64encode(f.read()).decode('utf-8')
                        sources.append({
                            "type": "inline",
                            "target": target_path,
                            "content": content,
                            "encoding": "base64"
                        })

    add_files('skills')
    add_files('workspace')

    payload = {
        "input": "Hello",
        "environment": {
            "config": {
                "sources": sources
            }
        },
        "agent": base_agent,
        "tools": tools,
        "stream": True
    }
    
    if instructions:
        payload["system_instruction"] = instructions
        
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    make_payload()
