#!/usr/bin/env python3
"""
Pre-render script: parse publications.bib + links.yml → _publications.yml

No external dependencies required — uses only the Python 3 standard library.

Workflow:
  1. Zotero (via Better BibTeX) exports/updates publications.bib
  2. You optionally add per-paper links in links.yml
  3. `quarto render` runs this script first, producing _publications.yml
  4. publications.qmd listing consumes that YAML automatically
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# BibTeX parser (regex-based, no external deps)
# ---------------------------------------------------------------------------

def parse_bib(path):
    """Parse a BibTeX file into a list of entry dicts."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    entries = []

    # Match @type{key, ... } — handles nested braces one level deep
    entry_re = re.compile(
        r"@(\w+)\s*\{\s*([^,]+?)\s*,(.+?)\n\}",
        re.DOTALL,
    )

    for m in entry_re.finditer(text):
        entry_type = m.group(1).lower()
        key = m.group(2).strip()
        body = m.group(3)
        raw_bibtex = m.group(0)  # full raw BibTeX entry

        fields = {}

        # field = {value} (value may contain one level of nested braces)
        field_re = re.compile(
            r"(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
        )
        for fm in field_re.finditer(body):
            fields[fm.group(1).lower()] = fm.group(2).strip()

        # field = number (unbraced integers, e.g. year = 2025)
        num_re = re.compile(r"(\w+)\s*=\s*(\d+)")
        for nm in num_re.finditer(body):
            fname = nm.group(1).lower()
            if fname not in fields:
                fields[fname] = nm.group(2)

        entries.append({"type": entry_type, "key": key, "fields": fields})

    return entries


# ---------------------------------------------------------------------------
# Minimal links.yml reader
# ---------------------------------------------------------------------------

def parse_links_yml(path):
    """
    Read the simple two-level links.yml format:

      CiteKey:
        doi: https://...
        code: https://...
    """
    if not os.path.exists(path):
        return {}

    links = {}
    current_key = None

    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # Top-level key (no leading whitespace)
            if not line[0].isspace() and stripped.endswith(":"):
                current_key = stripped[:-1].strip()
                links[current_key] = {}
            elif current_key and ":" in stripped:
                k, v = stripped.split(":", 1)
                links[current_key][k.strip()] = v.strip()

    return links


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_latex(text):
    """Strip common LaTeX markup from a string."""
    if not text:
        return ""
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\\&", "&", text)
    text = re.sub(r"\\copyright\{?\}?", "\u00a9", text)
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)  # generic \cmd{...}
    text = re.sub(r"\{([^}]*)\}", r"\1", text)  # remaining braces
    text = re.sub(r"~", " ", text)
    return text.strip()


def format_authors(raw):
    """Return a human-readable author string from BibTeX 'and'-separated names."""
    if not raw:
        return ""
    parts = [a.strip() for a in raw.split(" and ")]
    formatted = []
    for a in parts:
        if "," in a:
            last, first = a.split(",", 1)
            formatted.append(f"{first.strip()} {last.strip()}")
        else:
            formatted.append(a)
    return ", ".join(formatted)


def yaml_escape(text):
    """Escape a string for safe inclusion in double-quoted YAML."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


# Essential BibTeX fields (as seen on Google Scholar / publisher export)
BIBTEX_FIELDS = [
    "author", "title", "year", "journal", "booktitle",
    "volume", "number", "pages", "doi", "publisher",
]


def build_clean_bibtex(entry):
    """Reconstruct a minimal BibTeX entry with only essential fields."""
    lines = [f"@{entry['type']}{{{entry['key']},"]
    for field in BIBTEX_FIELDS:
        val = entry["fields"].get(field)
        if val:
            lines.append(f"  {field} = {{{val}}},")
    # Remove trailing comma on last field
    if len(lines) > 1:
        lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

LINK_TYPES = ["doi", "preprint", "code", "data", "osf", "github", "pdf"]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    bib_path = os.path.join(root, "publications.bib")
    links_path = os.path.join(root, "links.yml")
    out_path = os.path.join(root, "publications-listing.yml")

    if not os.path.exists(bib_path):
        print("bib_to_yaml.py: publications.bib not found, skipping.", file=sys.stderr)
        # Write empty file so Quarto listing doesn't error
        with open(out_path, "w") as f:
            f.write("[]\n")
        return

    entries = parse_bib(bib_path)
    links = parse_links_yml(links_path)

    items = []
    for entry in entries:
        f = entry["fields"]
        title = clean_latex(f.get("title", "Untitled"))
        author = format_authors(clean_latex(f.get("author", "")))
        year = f.get("year", "")
        journal = clean_latex(f.get("journal", f.get("booktitle", "")))
        doi = f.get("doi", "")
        abstract = clean_latex(f.get("abstract", ""))
        keywords = [
            k.strip() for k in f.get("keywords", "").split(",") if k.strip()
        ]
        volume = f.get("volume", "")
        number = f.get("number", "")
        pages = f.get("pages", "")

        item = {
            "key": entry["key"],
            "title": title,
            "author": author,
            "bibtex": build_clean_bibtex(entry),
            "year": year,
            "journal": journal,
            "volume": volume,
            "number": number,
            "pages": pages,
            "doi": doi,
            "abstract": abstract,
            "categories": keywords,
            "type": entry["type"],
        }

        # Merge per-paper links from links.yml
        paper_links = links.get(entry["key"], {})
        for lt in LINK_TYPES:
            if lt in paper_links:
                item[f"{lt}_url"] = paper_links[lt]

        # Fall back to DOI from bib entry if no explicit doi link
        if "doi_url" not in item and doi:
            item["doi_url"] = f"https://doi.org/{doi}"

        items.append(item)

    # Sort by year descending, then by first author
    items.sort(key=lambda x: (x.get("year", ""), x.get("author", "")), reverse=True)

    # Write YAML (manually — avoids PyYAML dependency)
    with open(out_path, "w", encoding="utf-8") as out:
        for item in items:
            out.write(f'- title: "{yaml_escape(item["title"])}"\n')
            out.write(f'  author: "{yaml_escape(item["author"])}"\n')
            out.write(f'  year: "{item["year"]}"\n')
            # Quarto listing uses 'date' for sorting
            out.write(f'  date: "{item["year"]}-01-01"\n')
            out.write(f'  journal: "{yaml_escape(item["journal"])}"\n')

            if item["volume"]:
                out.write(f'  volume: "{yaml_escape(item["volume"])}"\n')
            if item["number"]:
                out.write(f'  number: "{yaml_escape(item["number"])}"\n')
            if item["pages"]:
                out.write(f'  pages: "{yaml_escape(item["pages"])}"\n')

            if item["categories"]:
                out.write("  categories:\n")
                for cat in item["categories"]:
                    out.write(f'    - "{yaml_escape(cat)}"\n')

            if item["abstract"]:
                out.write(
                    f'  description: "{yaml_escape(item["abstract"])}"\n'
                )

            # Link URLs
            for lt in LINK_TYPES:
                url_key = f"{lt}_url"
                if item.get(url_key):
                    out.write(f'  {url_key}: "{item[url_key]}"\n')

            # Raw BibTeX for citation button (block scalar preserves formatting)
            if item.get("bibtex"):
                out.write("  bibtex: |\n")
                for line in item["bibtex"].splitlines():
                    out.write(f"    {line}\n")

            out.write("\n")

    print(f"bib_to_yaml.py: generated {len(items)} publication(s) → publications-listing.yml")


if __name__ == "__main__":
    main()
