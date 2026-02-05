#!/usr/bin/env python3
"""Check GlobalProtectVersions.json for new versions and update pan-gp.md accordingly.

Compares versions from the JSON source with the current state of pan-gp.md
in the endoflife-date/endoflife.date repository. Outputs an updated file
when newer versions are found.
"""

import argparse
import json
import re
import sys
from datetime import datetime


def parse_version(version_str):
    """Parse a GlobalProtect version string into a comparable tuple.

    Examples:
        "6.3.3-c842" -> (6, 3, 3, 842)
        "6.1.5"      -> (6, 1, 5, 0)
        "5.2.13-c418" -> (5, 2, 13, 418)
    """
    match = re.match(r"(\d+)\.(\d+)\.(\d+)(?:-c(\d+))?$", version_str)
    if not match:
        return None
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    build = int(match.group(4)) if match.group(4) else 0
    return (major, minor, patch, build)


def get_release_cycle(version_str):
    """Extract release cycle from version string.

    "6.3.3-c842" -> "6.3"
    """
    match = re.match(r"(\d+\.\d+)", version_str)
    return match.group(1) if match else None


def load_json_versions(json_path):
    """Load GlobalProtectVersions.json and find the latest version per release cycle.

    Returns dict: {"6.3": {"version": "6.3.3-c842", "date": "2025-12-17"}, ...}
    """
    raw = open(json_path, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig")
    entries = json.loads(text)

    cycles = {}
    for entry in entries:
        version_str = entry["version"]
        parsed = parse_version(version_str)
        if not parsed:
            continue

        cycle = get_release_cycle(version_str)
        if not cycle:
            continue

        released_date = datetime.strptime(
            entry["released-on"], "%Y/%m/%d %H:%M:%S"
        ).strftime("%Y-%m-%d")

        if cycle not in cycles or parsed > parse_version(cycles[cycle]["version"]):
            cycles[cycle] = {"version": version_str, "date": released_date}

    return cycles


def parse_md_releases(content):
    """Parse release blocks from pan-gp.md content using regex.

    Returns list of dicts with keys: releaseCycle, latest, latestReleaseDate,
    plus _start and _end offsets into the original content.
    """
    releases = []
    pattern = re.compile(
        r"^  - releaseCycle: \"([^\"]+)\".*?(?=\n  - releaseCycle:|\n---)",
        re.MULTILINE | re.DOTALL,
    )
    for match in pattern.finditer(content):
        block = match.group(0)
        cycle = match.group(1)

        def extract(field, text):
            m = re.search(rf"    {field}: (.+)", text)
            if not m:
                return None
            val = m.group(1).strip()
            return val.strip('"')

        releases.append(
            {
                "releaseCycle": cycle,
                "latest": extract("latest", block),
                "latestReleaseDate": extract("latestReleaseDate", block),
                "_start": match.start(),
                "_end": match.end(),
                "_text": block,
            }
        )
    return releases


def apply_updates(content, releases, json_cycles):
    """Apply version updates to the pan-gp.md content string.

    Returns (updated_content, list_of_change_descriptions).
    Only updates `latest` and `latestReleaseDate` — the link field is static
    per release cycle and does not contain version-specific components.
    """
    changes = []
    for release in reversed(releases):
        cycle = release["releaseCycle"]
        if cycle not in json_cycles:
            continue

        current_version = release["latest"] or ""
        new_version = json_cycles[cycle]["version"]
        new_date = json_cycles[cycle]["date"]

        current_parsed = parse_version(current_version) if current_version else (0, 0, 0, 0)
        new_parsed = parse_version(new_version)
        if not new_parsed or not (new_parsed > current_parsed):
            continue

        block = release["_text"]
        updated_block = block

        # Update latest
        updated_block = re.sub(
            r'(    latest: )"[^"]*"',
            rf'\g<1>"{new_version}"',
            updated_block,
        )
        # Update latestReleaseDate
        if "    latestReleaseDate:" in updated_block:
            updated_block = re.sub(
                r"(    latestReleaseDate: )\S+",
                rf"\g<1>{new_date}",
                updated_block,
            )
        else:
            # Insert latestReleaseDate after latest line if missing
            updated_block = re.sub(
                r'(    latest: "[^"]*")',
                rf"\1\n    latestReleaseDate: {new_date}",
                updated_block,
            )

        content = content[: release["_start"]] + updated_block + content[release["_end"] :]
        changes.append(f"{cycle}: {current_version} -> {new_version}")

    return content, changes


def main():
    parser = argparse.ArgumentParser(description="Update pan-gp.md with new GlobalProtect versions")
    parser.add_argument("--json", required=True, help="Path to GlobalProtectVersions.json")
    parser.add_argument("--md", required=True, help="Path to current pan-gp.md")
    parser.add_argument("--output", required=True, help="Path to write updated pan-gp.md")
    args = parser.parse_args()

    json_cycles = load_json_versions(args.json)
    with open(args.md, encoding="utf-8") as f:
        content = f.read()

    releases = parse_md_releases(content)
    updated_content, changes = apply_updates(content, releases, json_cycles)

    if not changes:
        print("NO_UPDATES")
        sys.exit(0)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("UPDATES_FOUND")
    for change in changes:
        print(change)


if __name__ == "__main__":
    main()
