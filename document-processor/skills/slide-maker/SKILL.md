---
name: slide-creator
description: Create Google-style presentation slides as standalone HTML files. Use when the user wants to (1) create presentation slides from notes or bullet points, (2) build slide decks in HTML format, (3) recreate or replicate existing slide designs, (4) convert rough notes or talking points into polished visual slides, or (5) needs professional Google-branded presentation materials with clean typography, visual diagrams, code blocks, or data visualizations.
---

# Google Slide Creator

Create professional, presentation-ready slides as standalone HTML files matching Google's internal presentation style. This skill is organized as a **component library** — pick a layout template, populate it with components, and wrap it in the presentation shell.

---

## 1. Output Format

The full presentation is a **single HTML file** containing all slides. Each slide is 1280×720px (16:9). The file includes built-in keyboard navigation (← → arrow keys), a slide counter, and smooth transitions. Open in any browser for presenting or screenshotting.

---

## 2. Mandatory Design System

Every slide MUST use these exact specifications.

### Presentation Shell

Wrap all slides in a presentation container. Each `.slide` is hidden by default; only `.slide.active` is visible.

```html
<div class="presentation">
  <div class="slide active"><!-- slide 1 --></div>
  <div class="slide"><!-- slide 2 --></div>
</div>
<div class="slide-counter">1 / 2</div>
```

```css
body { background: #f8f9fa; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
.presentation { position: relative; }
.slide {
  width: 1280px; height: 720px; background: #ffffff; border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 4px 12px rgba(0,0,0,0.06);
  padding: 48px 56px 40px; position: absolute; top: 0; left: 0;
  overflow: hidden; opacity: 0; pointer-events: none;
  transition: opacity 0.3s ease; display: flex; flex-direction: column;
}
.slide.active { position: relative; opacity: 1; pointer-events: auto; }
.slide::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 4px;
  background: linear-gradient(90deg, #4285f4, #34a853, #fbbc04, #ea4335);
}
```

### Navigation JavaScript

Always include at the bottom of `<body>`:

```javascript
<script>
  const slides = document.querySelectorAll('.slide');
  const counter = document.querySelector('.slide-counter');
  let current = 0;
  function showSlide(n) {
    slides[current].classList.remove('active');
    current = (n + slides.length) % slides.length;
    slides[current].classList.add('active');
    counter.textContent = (current + 1) + ' / ' + slides.length;
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === ' ') showSlide(current + 1);
    if (e.key === 'ArrowLeft') showSlide(current - 1);
  });
</script>
```

### Typography

- **Font**: Google Sans (headings, labels) + Google Sans Text (body). Load via Google Fonts:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Text:wght@400;500&display=swap" rel="stylesheet">
  ```
- **Add Google Sans Mono** when slides contain code blocks
- **Title (h1)**: 32–42px, font-weight 500, color `#202124`
- **Speaker line**: 14px, color `#5f6368`, placed above h1
- **Subtitle**: 15–17px, color `#5f6368`
- **Body text**: 14–18px, color `#3c4043`
- **Section labels**: 12–13px, uppercase, letter-spacing 0.5px, font-weight 500

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| text-primary | `#202124` | Headings, bold text |
| text-secondary | `#3c4043` | Body text |
| text-tertiary | `#5f6368` | Subtitles, labels, descriptions |
| text-muted | `#9aa0a6` | Captions, annotations |
| google-blue | `#1a73e8` | Links, highlighted labels, active states |
| google-green | `#34a853` | Success, positive, SOTA badges |
| google-yellow | `#fbbc04` | Caution, secondary highlights |
| google-red | `#ea4335` | Alerts, important badges |
| orange | `#e37400` | v2/future labels |
| border | `#e8eaed` | Card borders, dividers |
| border-light | `#dadce0` | Bullet dots, subtle borders |
| surface | `#f8f9fa` | Card backgrounds, diagram containers |

### Icons

Use **inline SVG heroicons** (outline style, stroke-based). Never use emojis. Standard icon size: 15–18px for chips, 18–22px for cards. Match stroke color to the section color context.

---

## 3. Layout Templates

Pick a layout template for each slide. These define the structural grid — components fill the zones.

### Template A: Title + Left/Right Split

The most common layout. Left column has text, right column has a visual component.

```
┌─────────────────────────────────────────────────────┐
│ Speaker line                                        │
│ Title (h1)                                          │
│                                                     │
│  ┌─ left-col (flex:1) ─┐  ┌─ right-col (400-460) ─┐│
│  │  Bullets / text /    │  │  Diagram / code /     ││
│  │  comparison cards    │  │  chart / mockup       ││
│  └──────────────────────┘  └───────────────────────┘│
│ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ │
└─────────────────────────────────────────────────────┘
```

- `.left-col { flex: 1 }` — `.right-col { flex: 0 0 400–460px }`
- Gap between columns: 44–60px

### Template B: Title + Full-Width Body

Full-width visual below the header. Use for grids, timelines, architecture diagrams.

```
┌─────────────────────────────────────────────────────┐
│ Speaker / Title                                     │
│                                                     │
│  ┌───────────── full-width body ──────────────────┐ │
│  │  Grid / Timeline / Tool cards / Architecture   │ │
│  └────────────────────────────────────────────────┘ │
│ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ │
└─────────────────────────────────────────────────────┘
```

### Template C: Hero Title (No Header)

No header bar. Title + subtitle + list on the left, right visual. Use for opening/closing slides.

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ┌─ left-col ──────────┐  ┌─ right-col ───────────┐│
│  │  Big Title (42px)   │  │  Code examples /      ││
│  │  Subtitle           │  │  hero visual          ││
│  │  Feature list       │  │                       ││
│  └─────────────────────┘  └───────────────────────┘│
│ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ │
└─────────────────────────────────────────────────────┘
```

### Template D: Side-by-Side Panels

Two equal-width panels for comparisons, before/after, or dual content.

```
┌─────────────────────────────────────────────────────┐
│ Speaker / Title                                     │
│                                                     │
│  ┌─ panel-left ────┐ ⟶  ┌─ panel-right ──────────┐│
│  │  OLD / Before   │    │  NEW / After            ││
│  │  (tinted bg)    │    │  (tinted bg)            ││
│  └─────────────────┘    └─────────────────────────┘│
│ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ │
└─────────────────────────────────────────────────────┘
```

---

## 4. Component Library

Pick components to fill the layout zones. Mix and match freely.

### 4.1 Diagram Components

#### Vertical Flow (Pipeline)

Numbered steps stacked vertically with CSS arrows connecting them. Best for: sequential processes, API lifecycles.

```html
<div class="flow">
  <div class="flow-step stage-1">
    <div class="step-icon">1</div>
    <div class="step-text">
      <div class="step-title">Step Name</div>
      <div class="step-desc">Brief description</div>
    </div>
  </div>
  <div class="flow-arrow"></div>
  <div class="flow-step stage-2">...</div>
</div>
```

- Wrap in `.diagram-container` (surface bg, border, rounded)
- Step icons: 36px circle, Google colors per stage (`.stage-1` blue, `.stage-2` yellow, `.stage-3` green, `.stage-4` red)
- Arrows: `::before` for line (2px), `::after` for triangle
- Optional: `.loop-badge` positioned absolute for agentic loops
- See: [example-bullets-flow-diagram.html](references/example-bullets-flow-diagram.html)

#### Horizontal Pipeline

Circular icon nodes connected by horizontal arrows. Best for: request lifecycles, data flows.

```html
<div class="pipeline">
  <div class="pipeline-step step-blue">
    <div class="step-circle"><svg>...</svg></div>
    <div class="step-label">Input</div>
    <div class="step-sublabel">Description</div>
  </div>
  <div class="pipeline-arrow"></div>
  <div class="pipeline-step step-green">...</div>
</div>
```

- Circle: 64px, 3px colored border, white bg, SVG icon inside
- Arrow: `::before` for line (36px wide), `::after` for triangle pointing right
- Hover: `scale(1.08)` + subtle box-shadow
- See: [example-horizontal-pipeline.html](references/example-horizontal-pipeline.html)

#### Hub & Spoke (Radial)

Central hub with nodes radiating outward. Best for: ecosystem views, tool relationships.

```html
<div class="hub-spoke">
  <svg class="spoke-lines"><!-- dashed lines from center to each node --></svg>
  <div class="hub">Central Label</div>
  <div class="spoke-node spoke-1"><!-- positioned absolute  --></div>
  <div class="spoke-node spoke-2">...</div>
</div>
```

- Hub: 120px circle, gradient bg, centered absolutely
- Spokes: SVG `<line>` elements with `stroke-dasharray="4 4"`
- Nodes: 130×68px cards, positioned with `top/left/right/bottom`, 6 positions around center
- See: [example-hub-spoke.html](references/example-hub-spoke.html)

#### Layered Architecture (Stacked Tiers)

Horizontal tiers stacked vertically with blocks inside each. Best for: system architecture, stack overviews.

```html
<div class="architecture">
  <div class="arch-layer layer-app">
    <div class="layer-label">APP</div>
    <div class="layer-content">
      <div class="arch-block">
        <div class="block-icon icon-blue"><svg>...</svg></div>
        <div class="block-text">
          <div class="block-name">SDK Name</div>
          <div class="block-desc">Description</div>
        </div>
      </div>
    </div>
  </div>
  <div class="layer-connector"></div>
  <div class="arch-layer layer-api">...</div>
</div>
```

- Layer: colored bg + border (blue/green/yellow/red), rotated side label via `writing-mode: vertical-rl`
- Blocks: white cards inside each layer, flex items
- Connector: down-pointing triangle centered between layers
- See: [example-layered-architecture.html](references/example-layered-architecture.html)

#### Swimlane Sequence

Multi-column sequence diagram with activity blocks crossing lanes. Best for: API call flows, interaction patterns, protocol sequences.

```html
<div class="swimlane-container">
  <div class="lane-headers">
    <div class="lane-header client">Client</div>
    <div class="lane-header server">Server</div>
    <div class="lane-header tools">Tools</div>
  </div>
  <div class="seq-rows">
    <div class="seq-row">
      <div class="seq-step step-blue"><div class="step-num">1</div></div>
      <div class="seq-lanes">
        <div class="seq-lane">
          <div class="activity activity-blue">Action description</div>
        </div>
        <div class="seq-lane"></div>
      </div>
    </div>
  </div>
</div>
```

- Headers: colored bottom border per lane
- Grid: left label column (140px) + lanes (flex)
- Activities: colored blocks with monospace code, positioned in the relevant lane
- Arrows: absolute-positioned triangles between lanes (`.arrow-right`, `.arrow-left`)
- See: [example-swimlane-sequence.html](references/example-swimlane-sequence.html)

#### Horizontal Timeline

Event dots along a horizontal track with content below each stop. Best for: evolution, roadmap, release history.

```html
<div class="timeline">
  <div class="timeline-item">
    <div class="timeline-dot dot-blue"><svg>...</svg></div>
    <div class="timeline-content">
      <div class="timeline-date">2024</div>
      <div class="timeline-title">Milestone</div>
      <div class="timeline-desc">Description</div>
      <span class="badge badge-ga">GA</span>
    </div>
  </div>
</div>
```

- Track: `::before` pseudo on `.timeline` (3px line, full width, `top: 24px`)
- Dots: 48px circle with SVG icon, colored shadow, positioned above content
- Content: centered text block below each dot
- See: [example-horizontal-timeline.html](references/example-horizontal-timeline.html)

### 4.2 Card Components

#### Numbered Card Grid (2×2 or 3-col)

Cards with big colored number badges. Best for: step-by-step guides, feature highlights.

```html
<div class="card-grid"> <!-- grid-template-columns: 1fr 1fr -->
  <div class="num-card card-1">
    <div class="card-top">
      <div class="card-num">1</div>
      <div class="card-title">Step Name</div>
    </div>
    <div class="card-desc">Description</div>
    <div class="card-detail"><span class="mono">code_example()</span></div>
  </div>
</div>
```

- Number badge: 40px rounded-square, Google color per card
- Detail row: auto-pushed to bottom via `margin-top: auto`, border-top separator
- See: [example-numbered-card-grid.html](references/example-numbered-card-grid.html)

#### Before/After Comparison Panels

Side-by-side panels with contrasting tints. Best for: old vs new, problem vs solution.

```html
<div class="compare-container">
  <div class="compare-panel panel-before">
    <div class="panel-header">
      <div class="panel-icon">✕ icon</div>
      <div class="panel-title">Old Way</div>
      <div class="panel-badge">OLD</div>
    </div>
    <ul class="panel-list"><li>Pain point with ✕ icon</li></ul>
    <div class="code-block">old code</div>
  </div>
  <div class="compare-arrow">→</div>
  <div class="compare-panel panel-after">
    <div class="panel-header">
      <div class="panel-icon">✓ icon</div>
      <div class="panel-title">New Way</div>
      <div class="panel-badge">NEW</div>
    </div>
    <ul class="panel-list"><li>Benefit with ✓ icon</li></ul>
    <div class="code-block">new code</div>
  </div>
</div>
```

- Before: yellow tint (`#fef7e0` bg), ✕ icons in orange
- After: green tint (`#e6f4ea` bg), ✓ icons in green
- Arrow circle between panels (40px, white bg with border)
- See: [example-before-after-comparison.html](references/example-before-after-comparison.html)

#### Comparison Cards (Inline)

Lighter-weight side-by-side cards within a column. Good for pros/cons within a Template A layout.

```html
<div class="h-layout">
  <div class="compare-card card-blue"><h3>Option A</h3><ul>...</ul></div>
  <div class="compare-card card-green"><h3>Option B</h3><ul>...</ul></div>
</div>
```

#### Tool Cards (3-col grid)

```html
<div class="tool-grid"> <!-- grid-template-columns: repeat(3, 1fr) -->
  <div class="tool-card">
    <div class="tool-icon"><svg>...</svg><span class="tool-name">Name</span></div>
    <div class="tool-desc">Description</div>
    <div class="tool-code">{"type": "name"}</div>
  </div>
</div>
```

#### Info Chips (Bottom Bar)

Compact metric/status chips. Use as a footer row below diagrams.

```html
<div class="info-chips">
  <div class="info-chip">
    <svg>icon</svg>
    <div class="chip-text"><strong>Label</strong> Description</div>
  </div>
</div>
```

### 4.3 Data Components

#### Code Blocks (Syntax-Highlighted)

Dark theme code blocks with manual `<span>` syntax highlighting.

```css
.code-block {
  background: #2d2d2d; border-radius: 12px; padding: 20px 22px;
  font-family: 'Google Sans Mono', monospace; font-size: 13px; line-height: 1.65;
  white-space: pre; overflow-x: auto;
}
```

Syntax colors: `.kw { color: #c792ea }` (keywords), `.fn { color: #82aaff }` (functions), `.st { color: #c3e88d }` (strings), `.op { color: #89ddff }` (operators), `.param { color: #f78c6c }` (params/bools), `.var { color: #eeffff }` (variables), `.cm { color: #9aa0a6 }` (comments).

- **Flush Left:** Code content inside `<div class="code-block">` must be flush left in the HTML file (no outer indentation).
- **Compact Closing:** Place the closing `</div>` on the same line as the final content to prevent trailing blank space.
- **Visibility Check:** Ensure content fits within containers and does not wrap unreadably. Code blocks should scroll horizontally if needed.


#### Tables

```html
<table class="data-table">
  <thead><tr><th>Column</th><th>Column</th></tr></thead>
  <tbody><tr><td>Value</td><td class="mono">code_value</td></tr></tbody>
</table>
```

Event tables (`.event-table`) use smaller text (11–12px) for dense data like streaming events.

#### Stat Cards (Benchmark Results)

Large number + name + badge. Score sizes: 28–32px bold. Color-code each benchmark differently.

#### Cost/Bar Charts

Horizontal bars on grey tracks with gradient fills. Include savings callout cards for key takeaways.

### 4.4 Text Components

#### Bullet List

```html
<ul class="bullet-list">
  <li><strong>Key point</strong> — supporting detail</li>
</ul>
```

- Dot: 8px circle via `::before`, colored (blue default)
- Gap: 14–16px between items

#### Chip Grid

```html
<div class="feature-group">
  <div class="section-label blue"><span class="dot"></span>Category</div>
  <div class="chip-grid">
    <div class="chip chip-blue"><svg>icon</svg> Feature name <span class="badge badge-ga">GA</span></div>
  </div>
</div>
```

- Chips: inline-flex, rounded, icon + text + optional badge
- Color variants: `.chip-blue`, `.chip-green`, `.chip-orange`, `.chip-red`

#### Callout Box

```html
<div class="callout callout-blue">
  <svg>icon</svg> <strong>Label:</strong> Message text with <code>inline code</code>.
</div>
```

- Tinted background + border matching the color scheme
- Variants: `.callout-blue`, `.callout-green`, `.callout-orange`

### 4.5 Badge System

```css
.badge { font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 3px; text-transform: uppercase; }
.badge-ga     { background: #e6f4ea; color: #137333; }  /* GA, SOTA */
.badge-new    { background: #e8f0fe; color: #1a73e8; }  /* NEW, Preview */
.badge-v2     { background: #fce8e6; color: #c5221f; }  /* v2, EAP */
.badge-orange { background: #fef7e0; color: #e37400; }  /* Coming, Future */
```

---

## 5. Workflow

1. Read the user's notes/talking points
2. Plan the slide breakdown — identify how many slides are needed
3. **For each slide**: pick a Layout Template (A–D), then select Components to fill its zones
4. Prioritize **visuals over text** — slides should communicate visually. Every slide should have at least one visual component
5. Keep bullet points concise (one line each when possible, max 5 per slide)
6. **Vary the layouts** — don't use the same template for every slide. Mix Template A with B, C, D across the deck
7. **Vary the visuals** — use different diagram types across slides (pipeline on one, hub-spoke on another, cards on a third)
8. Build a single HTML file with all slides inside `<div class="presentation">`, all CSS in one `<style>` block, and the navigation `<script>` at the bottom
9. Save as `<descriptive-name>-presentation.html` in the user's working directory
10. **Verify Layout Visibility:** Always check the rendered UI (using browser or screenshots) to ensure content is not cut off, overlapping, or wrapping unreadably. Code blocks must use horizontal scrolling for long lines.

---

## 6. Reference Examples

Read these complete, working HTML slides to understand the exact implementation. Each is a self-contained 1280×720 slide:

### Layout + Text Components
- [example-bullets-code-blocks.html](references/example-bullets-code-blocks.html) — Template C hero title + feature list left, two syntax-highlighted Python code blocks right
- [example-bullets-chat-mockup.html](references/example-bullets-chat-mockup.html) — Template A with bullets (NEW: badges) left, Gemini chat UI mockup right
- [example-quote-testimonial.html](references/example-quote-testimonial.html) — Template C variant without header, large quote mark visual + attribution
- [example-speaker-bio.html](references/example-speaker-bio.html) — Centered layout for profile intro, avatar, social icons, dot grid background
- [example-numbered-list-browser.html](references/example-numbered-list-browser.html) — Template A with numbered list left, browser window mockup right

### Diagram Components
- [example-bullets-flow-diagram.html](references/example-bullets-flow-diagram.html) — Template A with vertical pipeline flow diagram + resilience info chips
- [example-horizontal-pipeline.html](references/example-horizontal-pipeline.html) — Template B with horizontal left-to-right pipeline + detail chips below
- [example-hub-spoke.html](references/example-hub-spoke.html) — Template A with radial hub-and-spoke diagram (SVG spoke lines)
- [example-layered-architecture.html](references/example-layered-architecture.html) — Template B with 4-tier stacked architecture layers
- [example-swimlane-sequence.html](references/example-swimlane-sequence.html) — Template B with 3-lane swimlane sequence diagram
- [example-horizontal-timeline.html](references/example-horizontal-timeline.html) — Template B with horizontal timeline + summary chips
- [example-pipeline-stages.html](references/example-pipeline-stages.html) — Template B with horizontal stage cards + arrow connectors
- [example-input-output-funnel.html](references/example-input-output-funnel.html) — Template B with funnel diagram (SVG bezier curves)
- [example-stacked-category-rows.html](references/example-stacked-category-rows.html) — Template B with category bars + stacked items
- [example-agent-orchestrator.html](references/example-agent-orchestrator.html) — Template B with agent orchestrator flow diagram (SVG fork/join lines)
- [example-user-flow-agent.html](references/example-user-flow-agent.html) — Horizontal user flow diagram for agent lifecycle (dynamic paths)

### Card + Data Components
- [example-numbered-card-grid.html](references/example-numbered-card-grid.html) — Template B with 2×2 numbered step cards
- [example-before-after-comparison.html](references/example-before-after-comparison.html) — Template D with dual comparison panels (old vs new)
- [example-feature-grid-cost.html](references/example-feature-grid-cost.html) — Template A with chip grid left, cost bar chart + savings callout right
- [example-comparison-benchmarks.html](references/example-comparison-benchmarks.html) — Template A with comparison cards + benchmark stat cards
- [example-text-data-table.html](references/example-text-data-table.html) — Template A split-layout with structured data table + callout box
- [example-hero-stats.html](references/example-hero-stats.html) — Template B variant with large stats + gradient divider
- [example-key-changes-grid.html](references/example-key-changes-grid.html) — Template B with 3x2 grid of diff-style code blocks
- [example-fullwidth-code-block.html](references/example-fullwidth-code-block.html) — Template B with large-format code block
- [example-grouped-bar-chart.html](references/example-grouped-bar-chart.html) — Template B with multi-column benchmark bar chart


---

## 7. Anti-Patterns

- **Never use emojis** — always inline SVG heroicons
- **Never use Tailwind or external CSS** — all styles inlined in `<style>` block
- **Never exceed 1280×720** — slides must fit exactly
- **Never use placeholder images** — use CSS-drawn visuals, diagrams, code blocks
- **Never use generic colors** — always use the defined palette
- **Never crowd the slide** — prefer 3–5 bullet points max, let visuals do the talking
- **Never use `<br>` tags for spacing** — use proper margin/padding/gap
- **Never use the same layout for every slide** — vary templates across the deck
- **Never make a text-only slide** — every slide needs at least one visual component

---

## 8. PDF Export

To convert your HTML slides into a high-quality PDF with perfect 1280x720 dimensions, use the provided Python script.

### Usage

Run the script from the workspace root or the skill directory:

```bash
python3 skills/slide-creator/scripts/convert_to_pdf.py <URL_OR_FILE> [output.pdf]
```

### Examples

**Option A: Using the local dev server (Recommended)**
If you are running a local server (e.g., `python3 -m http.server 8000`):

```bash
python3 skills/slide-creator/scripts/convert_to_pdf.py http://localhost:8000/agent-creation-presentation.html output.pdf
```

**Option B: Using local file path**
If you want to convert the file directly without a server:

```bash
python3 skills/slide-creator/scripts/convert_to_pdf.py agent-creation-presentation.html output.pdf
```

### Requirements
- `google-chrome` must be available in your system path.
- The HTML file must include the `@media print` styles for proper layout (see Template setup).