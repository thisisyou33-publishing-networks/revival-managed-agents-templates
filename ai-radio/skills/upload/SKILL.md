---
name: upload
description: Upload the final podcast to Google Cloud Storage and provide a public download URL.
---

# Upload

Upload the final podcast audio file to Google Cloud Storage (GCS) so developers can download it via a public URL.

## Prerequisites

```bash
pip install google-cloud-storage
```

The agent's environment must have GCS credentials configured (via `GOOGLE_APPLICATION_CREDENTIALS`, default service account, or `gcloud auth`).

## Workflow

1. Read the final podcast file from `./workspace/audio/final/podcast.mp3`.
2. Upload it to a GCS bucket with a timestamped filename.
3. Make the file publicly accessible.
4. Return the public download URL.
5. Also copy the final file to `./workspace/output/` as a local backup.

## Python Code

```python
from google.cloud import storage
import os
import shutil
from datetime import datetime

def upload_podcast(
    local_path="./workspace/audio/final/podcast.mp3",
    bucket_name="YOUR_BUCKET_NAME",  # Replace with actual bucket
    prefix="podcasts/ai-radio"
):
    """Upload podcast to GCS and return public URL."""

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d")
    blob_name = f"{prefix}/{timestamp}-ai-radio.mp3"

    print(f"Uploading {local_path} to gs://{bucket_name}/{blob_name}...")

    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Upload with content type
    blob.upload_from_filename(local_path, content_type="audio/mpeg")

    # Make publicly accessible
    blob.make_public()

    public_url = blob.public_url
    print(f"✅ Uploaded successfully!")
    print(f"Public URL: {public_url}")

    return public_url

# Copy to output directory as well
os.makedirs("./workspace/output", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d")
output_filename = f"ai-radio-{timestamp}.mp3"
shutil.copy2(
    "./workspace/audio/final/podcast.mp3",
    f"./workspace/output/{output_filename}"
)
print(f"Local copy saved to ./workspace/output/{output_filename}")

# Upload to GCS
url = upload_podcast()
print(f"\n🎙️ Podcast available at: {url}")
```

## Alternative: Upload Without GCS

If GCS is not configured or the user prefers a different approach, offer these alternatives:

### Option A: Use Gemini Files API
Upload using the Gemini Files API, which is always available:

```python
from google import genai

client = genai.Client()

# Upload file
uploaded = client.files.upload(
    file="./workspace/audio/final/podcast.mp3",
    config={"display_name": f"AI Radio Podcast - {timestamp}"}
)
print(f"Uploaded to Gemini Files API: {uploaded.uri}")
print(f"Name: {uploaded.name}")
```

### Option B: Just Provide the Local File
If no cloud upload is possible, skip the upload and report the local file path:

```python
print("☁️ Cloud upload not configured.")
print(f"📁 Final podcast available locally at: ./workspace/output/{output_filename}")
print("To share it, you can manually upload to any file hosting service.")
```

## Bucket Configuration

If the user needs to create a GCS bucket:

```bash
# Create a bucket (run once)
gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=us-central1

# Set public access
gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET_NAME \
  --member=allUsers \
  --role=roles/storage.objectViewer
```

## Output

After upload, report to the user:

1. **Public download URL** (e.g., `https://storage.googleapis.com/bucket/podcasts/ai-radio/2026-04-27-ai-radio.mp3`)
2. **Local file path** (`./workspace/output/ai-radio-2026-04-27.mp3`)
3. **File size** in MB
4. **Duration** in minutes/seconds

## Error Handling

- If GCS upload fails, fall back to local file only and log the error.
- Always ensure the local copy in `./workspace/output/` exists regardless of upload outcome.
- Never let an upload failure mark the entire pipeline as failed — the podcast was already produced.
