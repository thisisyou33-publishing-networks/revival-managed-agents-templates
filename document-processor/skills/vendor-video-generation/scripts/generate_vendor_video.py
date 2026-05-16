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
"""Generate a video highlighting the highest-paid vendor from expense data.

Uses Veo for video generation with animated GIF fallback via Gemini image
generation and Pillow.

Usage:
    python3 generate_vendor_video.py --workspace ./workspace

Requires:
    pip install google-genai Pillow

Output:
    {workspace}/videos/top_vendor.mp4  (or .gif)
    {workspace}/data/top_vendor_summary.json
"""

import argparse
import base64
import csv
import io
import json
import os
import warnings
from google import genai

# Suppress experimental warnings from SDK
warnings.filterwarnings("ignore", message="Interactions usage is experimental")


def load_expense_data(workspace):
    """Load expense data from CSV or reconciliation JSON."""
    # Try reconciliation data first (richer data source)
    recon_path = os.path.join(workspace, "reconciliation_data.json")
    if os.path.exists(recon_path):
        print("Loading data from reconciliation_data.json...")
        with open(recon_path, "r") as f:
            recon_data = json.load(f)
        return recon_data.get("expenses", [])

    # Fall back to expenses.csv
    csv_path = os.path.join(workspace, "expenses.csv")
    if not os.path.exists(csv_path):
        print(f"❌ No expense data found at {csv_path}")
        return []

    print("Loading data from expenses.csv...")
    expenses = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["amount"] = float(row.get("amount", 0))
            except (ValueError, TypeError):
                row["amount"] = 0.0
            expenses.append(row)
    return expenses


def aggregate_by_vendor(expenses):
    """Aggregate expenses by vendor/merchant."""
    vendor_totals = {}
    for exp in expenses:
        merchant = exp.get("merchant", "Unknown").strip()
        amount = exp.get("amount", 0)
        if isinstance(amount, str):
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                amount = 0.0
        vendor_totals[merchant] = vendor_totals.get(merchant, 0) + amount

    # Sort by total descending
    sorted_vendors = sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_vendors


def generate_narrative(client, vendor_name, total_amount, percentage, total_spend):
    """Generate an executive narrative about the top vendor using Gemini."""
    print("Generating narrative summary...")

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        system_instruction=(
            "You are a concise financial analyst. Write a 2-3 sentence executive summary "
            "about a vendor's spending. Be professional and insightful. Focus on the scale "
            "of spending and potential implications."
        ),
        input=(
            f"Our highest-paid vendor is '{vendor_name}' with total payments of "
            f"${total_amount:,.2f}, representing {percentage:.1f}% of our total spend "
            f"of ${total_spend:,.2f}. Write a brief executive summary about this."
        ),
    )

    narrative = ""
    if hasattr(interaction, "steps") and interaction.steps and interaction.steps[-1].content:
        narrative = interaction.steps[-1].content[0].text

    print(f"✅ Narrative generated ({len(narrative)} chars)")
    return narrative


def try_veo_video(client, vendor_name, total_amount, output_dir):
    """Attempt video generation with Veo."""
    print("\nAttempting video generation with Veo...")

    prompt = (
        f"Create a short, professional business presentation video. "
        f"Show clean data visualization graphics and modern corporate motion design. "
        f"Display animated charts showing vendor spending analysis. "
        f"Use a sleek dark blue and white color scheme with smooth transitions. "
        f"Professional financial data presentation style."
    )

    try:
        interaction = client.interactions.create(
            model="veo-2.0-generate-preview",
            input=prompt,
            store=False,
        )

        for step in getattr(interaction, "steps", []):
            content_list = getattr(step, "content", [])
            for item in content_list:
                item_type = getattr(item, "type", "")
                mime_type = getattr(item, "mime_type", "")
                if item_type == "video" or (isinstance(mime_type, str) and mime_type.startswith("video/")):
                    video_data = base64.b64decode(item.data)
                    out_path = os.path.join(output_dir, "top_vendor.mp4")
                    with open(out_path, "wb") as f:
                        f.write(video_data)
                    size_kb = os.path.getsize(out_path) / 1024
                    print(f"✅ Video saved to {out_path} ({size_kb:.0f} KB)")
                    return out_path

        print("⚠️  No video returned from Veo.")
        return None

    except Exception as e:
        print(f"⚠️  Veo video generation failed: {e}")
        return None


def generate_gif_fallback(client, vendor_name, total_amount, percentage, output_dir):
    """Generate animated GIF from Gemini image frames as fallback."""
    print("\n🔄 Falling back to animated GIF generation...")

    frame_prompts = [
        (
            f"A clean, modern business infographic slide with dark blue background. "
            f"Large bold white text reading 'TOP VENDOR ANALYSIS'. "
            f"Subtle geometric patterns and professional corporate design. "
            f"Minimalist style, no people."
        ),
        (
            f"A professional data visualization slide with dark blue background. "
            f"A large stylized bar chart or pie chart showing vendor spending breakdown. "
            f"Clean corporate infographic style with blue and white color scheme. "
            f"Modern business analytics dashboard aesthetic."
        ),
        (
            f"A clean financial summary slide with dark blue background. "
            f"Display a large dollar amount in bold white text with a subtle upward arrow. "
            f"Professional corporate presentation style. "
            f"Clean, minimal design with geometric accents."
        ),
        (
            f"A professional business conclusion slide with dark blue gradient background. "
            f"Bold white text reading 'SPENDING INSIGHTS'. "
            f"Subtle data visualization elements in the background. "
            f"Modern corporate presentation style, clean and minimal."
        ),
    ]

    frames = []
    for i, prompt in enumerate(frame_prompts):
        print(f"  Generating frame {i + 1}/{len(frame_prompts)}...")
        try:
            interaction = client.interactions.create(
                model="gemini-3.1-flash-image-preview",
                input=prompt + " Image must be a 16:9 aspect ratio.",
                response_format={"type": "image"},
            )

            for step in getattr(interaction, "steps", []):
                content_list = getattr(step, "content", [])
                for item in content_list:
                    item_type = getattr(item, "type", "")
                    mime_type = getattr(item, "mime_type", "")
                    if item_type == "image" or (isinstance(mime_type, str) and mime_type.startswith("image/")):
                        image_data = base64.b64decode(item.data)
                        frames.append(image_data)
                        print(f"    ✅ Frame {i + 1} generated")
                        break

        except Exception as e:
            print(f"    ⚠️  Frame {i + 1} failed: {e}")

    if not frames:
        print("❌ No frames generated. Skipping GIF creation.")
        return None

    # Assemble GIF using Pillow
    try:
        from PIL import Image

        pil_frames = []
        for frame_data in frames:
            img = Image.open(io.BytesIO(frame_data))
            # Convert to RGB if needed (GIF doesn't support RGBA well)
            if img.mode != "RGB":
                img = img.convert("RGB")
            pil_frames.append(img)

        out_path = os.path.join(output_dir, "top_vendor.gif")
        pil_frames[0].save(
            out_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=2000,  # 2 seconds per frame
            loop=0,
        )
        size_kb = os.path.getsize(out_path) / 1024
        print(f"\n✅ Animated GIF saved to {out_path} ({size_kb:.0f} KB)")
        return out_path

    except ImportError:
        print("❌ Pillow not installed. Cannot create GIF.")
        return None
    except Exception as e:
        print(f"❌ GIF assembly failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate vendor video/GIF")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "dummy-key"))

    print("=== Document Processor: Vendor Video Generation ===\n")

    # Load expense data
    expenses = load_expense_data(args.workspace)
    if not expenses:
        print("❌ No expense data found. Exiting.")
        return

    print(f"Loaded {len(expenses)} expense records\n")

    # Aggregate by vendor
    sorted_vendors = aggregate_by_vendor(expenses)
    if not sorted_vendors:
        print("❌ No vendor data after aggregation. Exiting.")
        return

    total_spend = sum(v[1] for v in sorted_vendors)
    top_vendor_name, top_vendor_amount = sorted_vendors[0]
    top_vendor_pct = (top_vendor_amount / total_spend * 100) if total_spend > 0 else 0

    print(f"Top Vendor: {top_vendor_name}")
    print(f"Total Amount: ${top_vendor_amount:,.2f}")
    print(f"Percentage of Total Spend: {top_vendor_pct:.1f}%")
    print(f"Total Spend (all vendors): ${total_spend:,.2f}\n")

    # Generate narrative
    narrative = generate_narrative(client, top_vendor_name, top_vendor_amount, top_vendor_pct, total_spend)

    # Create output directory
    video_dir = os.path.join(args.workspace, "videos")
    os.makedirs(video_dir, exist_ok=True)

    # Try Veo first, then GIF fallback
    video_path = try_veo_video(client, top_vendor_name, top_vendor_amount, video_dir)

    if not video_path:
        video_path = generate_gif_fallback(
            client, top_vendor_name, top_vendor_amount, top_vendor_pct, video_dir
        )

    # Save summary JSON
    data_dir = os.path.join(args.workspace, "data")
    os.makedirs(data_dir, exist_ok=True)
    summary_path = os.path.join(data_dir, "top_vendor_summary.json")

    summary = {
        "vendor_name": top_vendor_name,
        "total_amount": top_vendor_amount,
        "percentage_of_total": round(top_vendor_pct, 2),
        "total_spend": total_spend,
        "narrative_summary": narrative,
        "video_path": video_path if video_path else None,
        "all_vendors": [{"name": v[0], "total": v[1]} for v in sorted_vendors[:10]],
    }

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Summary saved to {summary_path}")
    print(f"\n✅ Vendor video generation complete!")


if __name__ == "__main__":
    main()
