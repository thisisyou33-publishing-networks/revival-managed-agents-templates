#!/usr/bin/env python3
import argparse
import datetime
import html.parser
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

# Default configurations
MAX_PAGES = 50
USER_AGENT = "CustomerSupportScanner/1.0"

class HTMLToMarkdown(html.parser.HTMLParser):
    """A robust, standard HTML to Markdown converter."""
    def __init__(self):
        super().__init__()
        self.markdown = []
        self.current_tag = []
        self.link_href = None
        self.list_item_prefix = ""
        self.in_ignored_tag = False
        self.ignored_tags = {"script", "style", "head", "noscript", "iframe", "svg"}

    def handle_starttag(self, tag, attrs):
        if tag in self.ignored_tags:
            self.in_ignored_tag = True
            return
        
        self.current_tag.append(tag)
        attrs_dict = dict(attrs)

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.markdown.append(f"\n\n{'#' * level} ")
        elif tag == "p":
            self.markdown.append("\n\n")
        elif tag == "br":
            self.markdown.append("\n")
        elif tag == "li":
            self.markdown.append(f"\n{self.list_item_prefix}- ")
        elif tag == "ul":
            self.list_item_prefix += "  "
        elif tag == "ol":
            self.list_item_prefix += "  "
        elif tag == "strong" or tag == "b":
            self.markdown.append("**")
        elif tag == "em" or tag == "i":
            self.markdown.append("*")
        elif tag == "a":
            self.link_href = attrs_dict.get("href")
            self.markdown.append("[")

    def handle_endtag(self, tag):
        if tag in self.ignored_tags:
            self.in_ignored_tag = False
            return
            
        if self.current_tag and self.current_tag[-1] == tag:
            self.current_tag.pop()

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.markdown.append("\n")
        elif tag == "p":
            self.markdown.append("\n")
        elif tag == "ul" or tag == "ol":
            if len(self.list_item_prefix) >= 2:
                self.list_item_prefix = self.list_item_prefix[:-2]
        elif tag == "strong" or tag == "b":
            self.markdown.append("**")
        elif tag == "em" or tag == "i":
            self.markdown.append("*")
        elif tag == "a":
            if self.link_href:
                self.markdown.append(f"]({self.link_href})")
            else:
                self.markdown.append("]")
            self.link_href = None

    def handle_data(self, data):
        if self.in_ignored_tag:
            return
        # Clean up whitespace but retain useful text
        text = re.sub(r'\s+', ' ', data)
        if text.strip():
            self.markdown.append(text)

    def get_markdown(self):
        # Join pieces and clean up multiple blank lines
        result = "".join(self.markdown)
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()


def extract_links(html_content, base_url):
    """Finds all absolute links on a page that are within the same subdomain."""
    links = set()
    parsed_base = urllib.parse.urlparse(base_url)
    
    # Simple regex to find <a href="...">
    pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', re.IGNORECASE)
    for match in pattern.finditer(html_content):
        href = match.group(1).strip()
        # Resolve relative URLs
        absolute_url = urllib.parse.urljoin(base_url, href)
        # Clean up fragments/queries
        parsed_url = urllib.parse.urlparse(absolute_url)
        cleaned_url = urllib.parse.urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            "", "", "" # ignore params, query, fragment
        ))
        
        # Filter to make sure it's the same domain/subdomain
        if parsed_url.netloc == parsed_base.netloc:
            # Avoid binary/image assets
            _, ext = os.path.splitext(parsed_url.path.lower())
            if ext not in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mp3"}:
                links.add(cleaned_url)
    return links


def get_robots_parser(seed_url):
    """Fetches and parses robots.txt for the given seed URL."""
    parsed_url = urllib.parse.urlparse(seed_url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        print(f"Checking robot rules at: {robots_url}")
        req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=5) as response:
            rp.parse(response.read().decode("utf-8", errors="ignore").splitlines())
    except Exception as e:
        print(f"No robots.txt found or couldn't parse it: {e}. Proceeding with caution.")
        rp = None
    return rp


def sanitize_filename(url):
    """Creates a clean, flat filename for a given URL."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "home.md"
    # Replace non-alphanumeric with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', path)
    return f"{sanitized}.md"


def main():
    parser = argparse.ArgumentParser(description="Scan and analyze website for support corpus.")
    parser.add_argument("url", help="Seed URL to start analysis from")
    parser.add_argument("--force", action="store_true", help="Bypass 24-hour cache check")
    args = parser.parse_args()

    seed_url = args.url
    # Ensure scheme is present
    if not seed_url.startswith("http://") and not seed_url.startswith("https://"):
        seed_url = "https://" + seed_url

    workspace_dir = ".agents/workspace"
    pages_dir = os.path.join(workspace_dir, "pages")
    snapshots_file = os.path.join(workspace_dir, "snapshots.json")

    # Ensure directories exist
    os.makedirs(pages_dir, exist_ok=True)

    # 1. Caching check
    if not args.force and os.path.exists(snapshots_file):
        try:
            with open(snapshots_file, "r") as f:
                snapshots = json.load(f)
            
            if snapshots.get("seed_url") == seed_url:
                timestamp_str = snapshots.get("timestamp")
                if timestamp_str:
                    snapshot_time = datetime.datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    now = datetime.datetime.now(datetime.timezone.utc)
                    elapsed = now - snapshot_time
                    if elapsed < datetime.timedelta(days=1):
                        print(f"SUCCESS: Snapshot is up to date (created {timestamp_str}, which is less than 24 hours ago). Skipping scan.")
                        sys.exit(0)
        except Exception as e:
            print(f"Failed to read/parse snapshots.json: {e}. Forcing fresh scan.")

    # 2. Check Robots.txt
    rp = get_robots_parser(seed_url)
    if rp and not rp.can_fetch(USER_AGENT, seed_url):
        print(f"ERROR: Scanning disallowed by robots.txt for seed URL: {seed_url}")
        sys.exit(1)

    print(f"Starting deep website analysis of: {seed_url}")
    
    # BFS Queue
    urls_to_visit = [seed_url]
    visited_urls = set()
    pages_map = {}

    while urls_to_visit and len(visited_urls) < MAX_PAGES:
        url = urls_to_visit.pop(0)
        if url in visited_urls:
            continue

        if rp and not rp.can_fetch(USER_AGENT, url):
            print(f"Skipping {url} (disallowed by robots.txt)")
            continue

        print(f"Scanning [{len(visited_urls)+1}/{MAX_PAGES}]: {url}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as response:
                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    print(f"Skipping non-HTML content-type: {content_type}")
                    visited_urls.add(url)
                    continue
                
                html_bytes = response.read()
                html_content = html_bytes.decode("utf-8", errors="ignore")

            # Convert to Markdown
            converter = HTMLToMarkdown()
            converter.feed(html_content)
            markdown_content = converter.get_markdown()

            # Save the file
            filename = sanitize_filename(url)
            filepath = os.path.join(pages_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"---\noriginal_url: {url}\n---\n\n")
                f.write(markdown_content)

            pages_map[url] = f"pages/{filename}"
            visited_urls.add(url)

            # Extract and queue discovered links
            discovered_links = extract_links(html_content, url)
            for link in discovered_links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)

            # Politeness delay
            time.sleep(0.5)

        except Exception as e:
            print(f"Error scanning {url}: {e}")
            visited_urls.add(url)  # Mark as visited so we don't retry

    # Write snapshots.json
    snapshot_data = {
        "seed_url": seed_url,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "pages": pages_map
    }

    try:
        with open(snapshots_file, "w") as f:
            json.dump(snapshot_data, f, indent=2)
        print(f"SUCCESS: Analysis completed. Snapshots updated in {snapshots_file}")
    except Exception as e:
        print(f"ERROR: Failed to save snapshots.json: {e}")
        sys.exit(1)

    # 4. Generate pages/index.md (Structured Corpus Directory)
    index_filepath = os.path.join(pages_dir, "index.md")
    print(f"Generating structured directory index at: {index_filepath}")
    try:
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write("# Website Corpus Directory Index\n\n")
            f.write("This index lists and explains all specific support corpus Markdown files. Look up user questions in this index first to identify which file contains the relevant answer.\n\n")
            f.write("| Page Title / Topic | File Link | Original Source URL |\n")
            f.write("|---------------------|-----------|---------------------|\n")
            
            for url, relative_path in sorted(pages_map.items()):
                # Resolve full path to extract the first heading
                full_path = os.path.join(workspace_dir, relative_path)
                title = "Unknown Topic"
                try:
                    with open(full_path, "r", encoding="utf-8") as pf:
                        for line in pf:
                            # Skip frontmatter/meta and find first # heading
                            if line.strip().startswith("# "):
                                title = line.strip("# ").strip()
                                break
                except Exception:
                    pass
                
                # Format file path nicely for clicking
                filename = os.path.basename(relative_path)
                f.write(f"| {title} | [{filename}]({filename}) | [{url}]({url}) |\n")
        print(f"SUCCESS: Directory index generated successfully in {index_filepath}")
    except Exception as e:
        print(f"ERROR: Failed to generate directory index: {e}")


if __name__ == "__main__":
    main()
