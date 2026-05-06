#!/bin/bash
if [ -z "$GEMINI_API_KEY" ]; then
  echo "Error: GEMINI_API_KEY is not set."
  exit 1
fi

# Create temporary .env file
echo "GEMINI_API_KEY=$GEMINI_API_KEY" > .env

# Generate payload
python3 ../generate_payload.py "Generate a 2-minute radio show script about the top 3 stories on Hacker News today." > probers.json

# Send request (saving output to prober_output.log)
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "x-server-timeout: 600" \
  -d @probers.json > prober_output.log

# Clean up
rm probers.json
rm .env

