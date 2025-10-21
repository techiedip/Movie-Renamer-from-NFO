#!/usr/bin/env python3
"""
rename_from_nfo.py

Scan folders for .nfo files, extract the movie title, sanitize it
(replace ':' with '-', remove other special characters), and rename
the corresponding movie file(s) that share the same basename.

Usage:
    python3 rename_from_nfo.py /path/to/movies --recursive --dry-run
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List

# Movie file extensions to consider
MOVIE_EXTS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".mpg", ".mpeg", ".m4v", ".ts", ".webm", ".3gp", ".ogv"
}

# Allowed characters (we'll keep letters, numbers, spaces, dots, hyphens, underscores, parentheses)
_SANITIZE_RE = re.compile(r"[^A-Za-z0-9\s\.\-\_\(\)\[\]]+")

def extract_title_from_nfo(nfo_path: Path) -> Optional[str]:
    """
    Try multiple strategies to extract title from an .nfo:
    1) Parse as XML; search for <title>, <movietitle>, <originaltitle> tags (common).
    2) Regex search for <title>...</title> in raw text.
    3) Heuristic: look for a first non-empty line that looks like a title (as a fallback).
    Returns None if nothing found.
    """
    try:
        text = nfo_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        try:
            text = nfo_path.read_text(encoding="iso-8859-1", errors="replace")
        except Exception:
            return None

    # 1) Try XML parsing
    try:
        root = ET.fromstring(text.strip())
        # look for common tags
        for tag in ("title", "movietitle", "originaltitle", "name"):
            el = root.find(".//" + tag)
            if el is not None and el.text and el.text.strip():
                return el.text.strip()
    except ET.ParseError:
        # not strict XML - fall back to regex/heuristics
        pass

    # 2) Regex search for <title>...</title> (case-insensitive)
    m = re.search(r"(?i)<\s*title[^>]*>(.*?)<\s*/\s*title\s*>", text, re.DOTALL)
    if m:
        title = m.group(1).strip()
        # remove any internal tags
        title = re.sub(r"<[^>]+>", "", title).strip()
        if title:
            return title

    # 3) Look for lines like "Title: ...", "MOVIE: ..." etc.
    for line in text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        # common metadata patterns
        m2 = re.match(r"(?i)^(?:title|movie title|moviename|name)\s*[:=]\s*(.+)$", ln)
        if m2:
            t = m2.group(1).strip()
            if t:
                return t

    # 4) Fallback: first non-empty line that's not an obvious xml tag
    for line in text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        if ln.startswith("<"):  # looks like a tag -> skip
            continue
        # remove surrounding quotes if any, and return
        ln = ln.strip(' "\'')
        if len(ln) >= 2:
            return ln

    return None

def sanitize_title(title: str) -> str:
    """
    Sanitizes the title:
    - Replace ':' with '-'
    - Remove disallowed special characters (per _SANITIZE_RE)
    - Collapse multiple spaces to one
    - Trim
    """
    t = title.replace(":", "-")
    # Insert space after '-' if followed by an alphabet character
    t = re.sub(r"-(?=[A-Za-z0-9])", "- ", t)
    # Insert space before '-' if preceded by an alphabet character
    t = re.sub(r"([A-Za-z0-9])-", r"\1 -", t)
    # Some NFOs may include HTML entities - decode common ones (basic)
    t = t.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    # Remove other special characters
    t = _SANITIZE_RE.sub("", t)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    # Optionally, limit length (not strictly requested) - omitted; could add if desired
    return t

def find_movie_files_with_basename(dirpath: Path, base: str) -> List[Path]:
    """
    Return list of movie files in dirpath whose stem matches base.
    Matching is case-insensitive.
    Also handles files like "My.Movie.2020.mkv" vs nfo "My Movie 2020.nfo" by comparing stems ignoring punctuation.
    """
    results = []
    base_lower = base.lower()
    # two matching strategies:
    # 1) filename stem exactly equals base (case-insensitive)
    # 2) a looser normalized compare: remove non-alnum and compare
    def normalize(s: str) -> str:
        return re.sub(r"[^A-Za-z0-9]+", "", s).lower()

    norm_base = normalize(base)

    for p in dirpath.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() in MOVIE_EXTS:
            stem = p.stem
            if stem.lower() == base_lower:
                results.append(p)
                continue
            if normalize(stem) == norm_base:
                results.append(p)
                continue
    return results

def unique_target(dest: Path) -> Path:
    """
    If dest exists, append (1), (2), ... before suffix until unique.
    """
    if not dest.exists():
        return dest
    parent = dest.parent
    stem = dest.stem
    suffix = dest.suffix
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def main(root: Path, recursive: bool, dry_run: bool, do_yes: bool):
    nfo_paths = []
    if recursive:
        for p in root.rglob("*.nfo"):
            nfo_paths.append(p)
    else:
        for p in root.glob("*.nfo"):
            nfo_paths.append(p)

    if not nfo_paths:
        print("No .nfo files found (in {}{}).".format(root, " (recursive)" if recursive else ""))
        return

    actions = []
    for nfo in nfo_paths:
        base = nfo.stem
        title = extract_title_from_nfo(nfo)
        if not title:
            print(f"[WARN] Could not extract title from {nfo}")
            continue
        sanitized = sanitize_title(title)
        if not sanitized:
            print(f"[WARN] Title extracted from {nfo} is empty after sanitization. Raw: {title!r}")
            continue

        dirpath = nfo.parent
        movie_files = find_movie_files_with_basename(dirpath, base)
        if not movie_files:
            print(f"[WARN] No movie files found matching basename '{base}' for NFO {nfo}")
            continue

        for mf in movie_files:
            new_name = f"{sanitized}{mf.suffix}"
            target = dirpath / new_name
            unique = unique_target(target)
            if mf.resolve() == unique.resolve():
                print(f"[SKIP] {mf} already has desired name.")
                continue
            actions.append((mf, unique, nfo, title, sanitized))

    if not actions:
        print("No renames to perform.")
        return

    print(f"\nPlanned actions ({len(actions)}):")
    for src, dst, nfo, raw_title, sanitized in actions:
        print(f"  {src.name}  ->  {dst.name}  (from NFO: {nfo.name} | raw title: {raw_title})")

    if dry_run:
        print("\nDry run mode; no files were renamed. To perform renames rerun without --dry-run and add --yes to confirm.")
        return

    if not do_yes:
        # Ask confirmation interactively
        try:
            resp = input("\nProceed with renaming? [y/N]: ").strip().lower()
        except KeyboardInterrupt:
            print("\nCancelled.")
            return
        if resp not in ("y", "yes"):
            print("Aborted by user.")
            return

    # Perform renames
    for src, dst, nfo, raw_title, sanitized in actions:
        try:
            dst_parent = dst.parent
            # ensure the parent exists (it does)
            src.rename(dst)
            print(f"[OK] Renamed: {src.name} -> {dst.name}")
        except Exception as e:
            print(f"[ERROR] Failed to rename {src} -> {dst}: {e}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Rename movie files using titles from .nfo files.")
    ap.add_argument("path", help="Folder to scan for .nfo files")
    ap.add_argument("--recursive", "-r", action="store_true", help="Scan folders recursively")
    ap.add_argument("--dry-run", "-n", action="store_true", help="Show what would be done but don't rename files")
    ap.add_argument("--yes", "-y", action="store_true", help="Don't prompt, just perform renames")
    args = ap.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print("Path does not exist or is not a directory:", root)
        sys.exit(1)

    main(root, args.recursive, args.dry_run, args.yes)
