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
"""Generate a self-contained HTML slideshow of the top highest-cost vendors.

Usage:
    python3 generate_slideshow.py --workspace ./workspace
    python3 generate_slideshow.py --workspace ./workspace --top 5

Requires:
    pip install google-genai

Output:
    {workspace}/reports/vendor_slideshow.html
"""

import argparse
import csv
import html
import json
import os
import warnings
from datetime import datetime
from google import genai

# Suppress experimental warnings from SDK
warnings.filterwarnings("ignore", message="Interactions usage is experimental")


def load_expenses(csv_path):
    """Load expenses from CSV file."""
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


def aggregate_vendors(expenses, top_n):
    """Aggregate expenses by vendor and return top N with details."""
    vendor_data = {}
    for exp in expenses:
        merchant = exp.get("merchant", "Unknown").strip()
        amount = exp.get("amount", 0)
        category = exp.get("category", "Uncategorized").strip()

        if merchant not in vendor_data:
            vendor_data[merchant] = {
                "total": 0,
                "count": 0,
                "categories": {},
            }

        vendor_data[merchant]["total"] += amount
        vendor_data[merchant]["count"] += 1
        vendor_data[merchant]["categories"][category] = (
            vendor_data[merchant]["categories"].get(category, 0) + amount
        )

    grand_total = sum(v["total"] for v in vendor_data.values())

    # Sort by total descending and take top N
    sorted_vendors = sorted(vendor_data.items(), key=lambda x: x[1]["total"], reverse=True)[:top_n]

    result = []
    for name, data in sorted_vendors:
        pct = (data["total"] / grand_total * 100) if grand_total > 0 else 0
        result.append({
            "name": name,
            "total": data["total"],
            "percentage": pct,
            "count": data["count"],
            "categories": data["categories"],
        })

    return result, grand_total, len(vendor_data)


def generate_vendor_insight(client, vendor_name, total, percentage, categories):
    """Generate an AI insight for a vendor using Gemini."""
    cat_breakdown = ", ".join(
        f"{cat}: ${amt:,.2f}" for cat, amt in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
    )

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        system_instruction=(
            "You are a concise financial analyst. Write exactly 2-3 sentences of executive insight "
            "about this vendor's spending. Be professional, analytical, and actionable. "
            "Do not use markdown formatting."
        ),
        input=(
            f"Vendor: {vendor_name}\n"
            f"Total Spend: ${total:,.2f} ({percentage:.1f}% of total)\n"
            f"Category Breakdown: {cat_breakdown}\n"
            f"Provide a brief executive insight about this vendor's spending pattern."
        ),
    )

    insight = ""
    if hasattr(interaction, "steps") and interaction.steps and interaction.steps[-1].content:
        insight = interaction.steps[-1].content[0].text.strip()

    return insight


def build_category_bars_svg(categories, max_amount):
    """Build inline SVG horizontal bars for category breakdown."""
    if not categories:
        return ""

    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
    bar_height = 28
    spacing = 8
    label_width = 140
    bar_area_width = 300
    total_height = len(sorted_cats) * (bar_height + spacing)

    svg_parts = [
        f'<svg width="100%" viewBox="0 0 {label_width + bar_area_width + 80} {total_height}" '
        f'xmlns="http://www.w3.org/2000/svg" style="max-width: 520px;">'
    ]

    for i, (cat, amount) in enumerate(sorted_cats):
        y = i * (bar_height + spacing)
        bar_width = (amount / max_amount * bar_area_width) if max_amount > 0 else 0
        escaped_cat = html.escape(cat)

        svg_parts.append(
            f'<text x="0" y="{y + bar_height * 0.7}" '
            f'fill="rgba(255,255,255,0.7)" font-size="12" font-family="Inter, sans-serif">'
            f'{escaped_cat}</text>'
        )
        svg_parts.append(
            f'<rect x="{label_width}" y="{y + 2}" width="{bar_width}" height="{bar_height - 4}" '
            f'rx="4" fill="url(#barGrad)" opacity="0.9"/>'
        )
        svg_parts.append(
            f'<text x="{label_width + bar_width + 8}" y="{y + bar_height * 0.7}" '
            f'fill="rgba(255,255,255,0.9)" font-size="12" font-family="Inter, sans-serif">'
            f'${amount:,.0f}</text>'
        )

    svg_parts.append(
        '<defs><linearGradient id="barGrad" x1="0%" y1="0%" x2="100%" y2="0%">'
        '<stop offset="0%" stop-color="#7c3aed"/>'
        '<stop offset="100%" stop-color="#2563eb"/>'
        '</linearGradient></defs>'
    )
    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def build_comparison_chart_svg(vendors):
    """Build inline SVG comparison bar chart for the summary slide."""
    if not vendors:
        return ""

    max_total = max(v["total"] for v in vendors)
    bar_width = 80
    spacing = 40
    chart_width = len(vendors) * (bar_width + spacing)
    chart_height = 250
    label_area = 60

    svg_parts = [
        f'<svg width="100%" viewBox="0 0 {chart_width + 40} {chart_height + label_area + 20}" '
        f'xmlns="http://www.w3.org/2000/svg" style="max-width: 600px; margin: 0 auto; display: block;">'
    ]

    # Gradient definition
    svg_parts.append(
        '<defs>'
        '<linearGradient id="chartGrad" x1="0%" y1="100%" x2="0%" y2="0%">'
        '<stop offset="0%" stop-color="#7c3aed"/>'
        '<stop offset="100%" stop-color="#2563eb"/>'
        '</linearGradient>'
        '</defs>'
    )

    for i, vendor in enumerate(vendors):
        x = 20 + i * (bar_width + spacing)
        bar_height_val = (vendor["total"] / max_total * chart_height) if max_total > 0 else 0
        y = chart_height - bar_height_val
        escaped_name = html.escape(vendor["name"])

        # Bar
        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height_val}" '
            f'rx="6" fill="url(#chartGrad)" opacity="0.9"/>'
        )
        # Amount label
        svg_parts.append(
            f'<text x="{x + bar_width / 2}" y="{y - 8}" text-anchor="middle" '
            f'fill="rgba(255,255,255,0.9)" font-size="13" font-weight="600" '
            f'font-family="Inter, sans-serif">${vendor["total"]:,.0f}</text>'
        )
        # Vendor name label (below bar)
        svg_parts.append(
            f'<text x="{x + bar_width / 2}" y="{chart_height + 20}" text-anchor="middle" '
            f'fill="rgba(255,255,255,0.7)" font-size="11" font-family="Inter, sans-serif">'
            f'{escaped_name[:18]}</text>'
        )
        # Percentage label
        svg_parts.append(
            f'<text x="{x + bar_width / 2}" y="{chart_height + 38}" text-anchor="middle" '
            f'fill="rgba(255,255,255,0.5)" font-size="10" font-family="Inter, sans-serif">'
            f'{vendor["percentage"]:.1f}%</text>'
        )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def build_html(vendors, grand_total, total_vendor_count, report_date):
    """Build the complete self-contained HTML slideshow."""

    # Build vendor slides HTML
    vendor_slides = []
    for i, vendor in enumerate(vendors):
        escaped_name = html.escape(vendor["name"])
        rank = i + 1
        max_cat_amount = max(vendor["categories"].values()) if vendor["categories"] else 1
        category_svg = build_category_bars_svg(vendor["categories"], max_cat_amount)
        escaped_insight = html.escape(vendor.get("insight", ""))

        vendor_slides.append(f"""
        <div class="slide">
            <div class="slide-content">
                <div class="rank-badge">#{rank}</div>
                <h2 class="vendor-name">{escaped_name}</h2>
                <div class="stats-row">
                    <div class="stat-card">
                        <div class="stat-value">${vendor['total']:,.2f}</div>
                        <div class="stat-label">Total Spend</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{vendor['percentage']:.1f}%</div>
                        <div class="stat-label">of Total Spend</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{vendor['count']}</div>
                        <div class="stat-label">Transactions</div>
                    </div>
                </div>
                <div class="category-section">
                    <h3>Category Breakdown</h3>
                    {category_svg}
                </div>
                <blockquote class="insight-quote">
                    <p>{escaped_insight}</p>
                </blockquote>
            </div>
        </div>""")

    vendor_slides_html = "\n".join(vendor_slides)

    # Build comparison chart
    comparison_svg = build_comparison_chart_svg(vendors)

    # Build dot indicators
    total_slides = len(vendors) + 2  # title + vendors + summary
    dots_html = "\n".join(
        f'<span class="dot{" active" if i == 0 else ""}" data-index="{i}"></span>'
        for i in range(total_slides)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Vendor Cost Analysis - Top {len(vendors)} highest-cost vendors slideshow report">
    <title>Vendor Cost Analysis</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0f0f1a;
            color: #fff;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            cursor: pointer;
            user-select: none;
        }}

        .slideshow {{
            position: relative;
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }}

        .slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transform: translateX(60px);
            transition: opacity 0.6s ease, transform 0.6s ease;
            pointer-events: none;
            padding: 40px;
        }}

        .slide.active {{
            opacity: 1;
            transform: translateX(0);
            pointer-events: auto;
        }}

        .slide.exit {{
            opacity: 0;
            transform: translateX(-60px);
        }}

        .slide-content {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 48px;
            max-width: 800px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
        }}

        /* Title Slide */
        .title-slide .slide-content {{
            text-align: center;
            background: rgba(255, 255, 255, 0.03);
        }}

        .title-slide h1 {{
            font-size: 3em;
            font-weight: 800;
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
            letter-spacing: -1px;
        }}

        .title-slide .subtitle {{
            font-size: 1.1em;
            color: rgba(255, 255, 255, 0.5);
            margin-bottom: 40px;
        }}

        .title-stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
        }}

        .title-stat {{
            text-align: center;
        }}

        .title-stat .value {{
            font-size: 2em;
            font-weight: 700;
            color: #fff;
        }}

        .title-stat .label {{
            font-size: 0.85em;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 4px;
        }}

        /* Vendor Slides */
        .rank-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            color: #fff;
            font-size: 1em;
            font-weight: 700;
            padding: 6px 16px;
            border-radius: 20px;
            margin-bottom: 16px;
        }}

        .vendor-name {{
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 24px;
            letter-spacing: -0.5px;
        }}

        .stats-row {{
            display: flex;
            gap: 16px;
            margin-bottom: 28px;
            flex-wrap: wrap;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 16px 20px;
            flex: 1;
            min-width: 120px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.4em;
            font-weight: 700;
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            font-size: 0.8em;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 4px;
        }}

        .category-section {{
            margin-bottom: 24px;
        }}

        .category-section h3 {{
            font-size: 0.9em;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
        }}

        .insight-quote {{
            border-left: 3px solid #7c3aed;
            padding: 12px 20px;
            background: rgba(124, 58, 237, 0.08);
            border-radius: 0 12px 12px 0;
            margin-top: 8px;
        }}

        .insight-quote p {{
            font-size: 0.95em;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.6;
            font-style: italic;
        }}

        /* Summary Slide */
        .summary-slide .slide-content {{
            text-align: center;
        }}

        .summary-slide h2 {{
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .summary-subtitle {{
            color: rgba(255, 255, 255, 0.5);
            margin-bottom: 32px;
        }}

        .chart-container {{
            margin: 24px 0;
        }}

        /* Navigation Dots */
        .dots {{
            position: fixed;
            bottom: 28px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            z-index: 100;
        }}

        .dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            cursor: pointer;
            transition: background 0.3s ease, transform 0.3s ease;
        }}

        .dot.active {{
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            transform: scale(1.3);
        }}

        .dot:hover {{
            background: rgba(255, 255, 255, 0.4);
        }}

        /* Background decoration */
        .bg-glow {{
            position: fixed;
            width: 400px;
            height: 400px;
            border-radius: 50%;
            filter: blur(120px);
            opacity: 0.15;
            pointer-events: none;
            z-index: -1;
        }}

        .bg-glow-1 {{
            top: -100px;
            right: -100px;
            background: #7c3aed;
        }}

        .bg-glow-2 {{
            bottom: -100px;
            left: -100px;
            background: #2563eb;
        }}

        /* Scrollbar styling for overflow content */
        .slide-content::-webkit-scrollbar {{
            width: 4px;
        }}

        .slide-content::-webkit-scrollbar-track {{
            background: transparent;
        }}

        .slide-content::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div class="bg-glow bg-glow-1"></div>
    <div class="bg-glow bg-glow-2"></div>

    <div class="slideshow" id="slideshow">
        <!-- Title Slide -->
        <div class="slide title-slide active">
            <div class="slide-content">
                <h1>Vendor Cost Analysis</h1>
                <p class="subtitle">Report generated {html.escape(report_date)}</p>
                <div class="title-stats">
                    <div class="title-stat">
                        <div class="value">${grand_total:,.0f}</div>
                        <div class="label">Total Spend</div>
                    </div>
                    <div class="title-stat">
                        <div class="value">{total_vendor_count}</div>
                        <div class="label">Vendors</div>
                    </div>
                    <div class="title-stat">
                        <div class="value">{len(vendors)}</div>
                        <div class="label">Featured</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Vendor Slides -->
        {vendor_slides_html}

        <!-- Summary Slide -->
        <div class="slide summary-slide">
            <div class="slide-content">
                <h2>Vendor Comparison</h2>
                <p class="summary-subtitle">Top {len(vendors)} vendors by total spend</p>
                <div class="chart-container">
                    {comparison_svg}
                </div>
                <p style="margin-top: 24px; color: rgba(255,255,255,0.5); font-size: 0.9em;">
                    Total analyzed spend: ${grand_total:,.2f} across {total_vendor_count} vendors
                </p>
            </div>
        </div>
    </div>

    <div class="dots" id="dots">
        {dots_html}
    </div>

    <script>
        (function() {{
            var currentSlide = 0;
            var slides = document.querySelectorAll('.slide');
            var dots = document.querySelectorAll('.dot');
            var totalSlides = slides.length;
            var autoAdvanceInterval = null;
            var isPaused = false;

            function goToSlide(index) {{
                if (index < 0) index = totalSlides - 1;
                if (index >= totalSlides) index = 0;

                slides[currentSlide].classList.remove('active');
                slides[currentSlide].classList.add('exit');
                dots[currentSlide].classList.remove('active');

                setTimeout(function() {{
                    slides[currentSlide].classList.remove('exit');
                    currentSlide = index;
                    slides[currentSlide].classList.add('active');
                    dots[currentSlide].classList.add('active');
                }}, 100);
            }}

            function nextSlide() {{
                goToSlide(currentSlide + 1);
            }}

            function prevSlide() {{
                goToSlide(currentSlide - 1);
            }}

            function startAutoAdvance() {{
                if (autoAdvanceInterval) clearInterval(autoAdvanceInterval);
                autoAdvanceInterval = setInterval(function() {{
                    if (!isPaused) nextSlide();
                }}, 8000);
            }}

            // Keyboard navigation
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'ArrowRight' || e.key === ' ') {{
                    nextSlide();
                    startAutoAdvance();
                }} else if (e.key === 'ArrowLeft') {{
                    prevSlide();
                    startAutoAdvance();
                }}
            }});

            // Click to advance
            document.getElementById('slideshow').addEventListener('click', function() {{
                nextSlide();
                startAutoAdvance();
            }});

            // Dot click navigation
            dots.forEach(function(dot) {{
                dot.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    var index = parseInt(this.getAttribute('data-index'));
                    goToSlide(index);
                    startAutoAdvance();
                }});
            }});

            // Pause on hover
            document.getElementById('slideshow').addEventListener('mouseenter', function() {{
                isPaused = true;
            }});

            document.getElementById('slideshow').addEventListener('mouseleave', function() {{
                isPaused = false;
            }});

            // Start auto-advance
            startAutoAdvance();
        }})();
    </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate vendor cost slideshow")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    parser.add_argument("--top", type=int, default=3, help="Number of top vendors to feature")
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "dummy-key"))

    print("=== Document Processor: Vendor Slideshow ===\n")

    # Load expenses
    csv_path = os.path.join(args.workspace, "expenses.csv")
    if not os.path.exists(csv_path):
        print(f"❌ Expenses file not found at {csv_path}")
        return

    expenses = load_expenses(csv_path)
    print(f"Loaded {len(expenses)} expenses from {csv_path}")

    # Aggregate vendors
    vendors, grand_total, total_vendor_count = aggregate_vendors(expenses, args.top)
    if not vendors:
        print("❌ No vendor data after aggregation. Exiting.")
        return

    print(f"Grand total: ${grand_total:,.2f} across {total_vendor_count} vendors")
    print(f"Featuring top {len(vendors)} vendors:\n")

    for i, v in enumerate(vendors):
        print(f"  #{i + 1} {v['name']}: ${v['total']:,.2f} ({v['percentage']:.1f}%)")

    # Generate AI insights for each vendor
    print("\nGenerating AI insights...")
    for i, vendor in enumerate(vendors):
        try:
            print(f"  [{i + 1}/{len(vendors)}] {vendor['name']}...")
            insight = generate_vendor_insight(
                client, vendor["name"], vendor["total"],
                vendor["percentage"], vendor["categories"]
            )
            vendor["insight"] = insight
            print(f"    ✅ Insight generated")
        except Exception as e:
            print(f"    ⚠️  Insight generation failed: {e}")
            vendor["insight"] = (
                f"{vendor['name']} represents {vendor['percentage']:.1f}% of total vendor spend "
                f"with ${vendor['total']:,.2f} across {vendor['count']} transactions."
            )

    # Build HTML
    print("\nBuilding HTML slideshow...")
    report_date = datetime.now().strftime("%B %d, %Y")
    html_content = build_html(vendors, grand_total, total_vendor_count, report_date)

    # Write output
    out_dir = os.path.join(args.workspace, "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "vendor_slideshow.html")

    with open(out_path, "w") as f:
        f.write(html_content)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"\n✅ Slideshow saved to {out_path} ({size_kb:.1f} KB)")
    print(f"   {len(vendors) + 2} slides (title + {len(vendors)} vendors + summary)")
    print(f"\n✅ Vendor slideshow generation complete!")


if __name__ == "__main__":
    main()
