#!/usr/bin/env python3
"""Materialize the fresh S8-b development task templates (no model calls)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = [
 ("a01_label_fields","Parse semicolon-delimited key=value fields","Trim both sides, split only at the first equals sign, discard blank keys or values, and retain later duplicate keys."),
 ("a02_config_lines","Parse configuration lines","Ignore blank/comment lines, trim key/value whitespace, split only at the first colon, and retain the last value for duplicate keys."),
 ("a03_version_parts","Normalize version components","Accept an optional v prefix, require dot-separated non-negative integer components, and return a three-component tuple with missing parts set to zero."),
 ("a04_duration_units","Convert duration text to seconds","Accept whitespace-separated integer unit fragments using s, m, h, or d; reject malformed fragments and sum repeated units."),
 ("a05_safe_extension","Extract a safe filename extension","Return the lower-case final extension without the dot; dotfiles, names without extensions, and trailing dots have no extension."),
 ("a06_date_format","Normalize calendar dates","Accept YYYY-MM-DD or YYYY/MM/DD, validate the calendar date, and return YYYY-MM-DD; invalid values return None."),
 ("a07_path_segments","Normalize relative path segments","Collapse empty and dot segments, reject any traversal segment, and return slash-joined safe segments."),
 ("a08_header_names","Canonicalize a header name","Trim, lower-case, replace punctuation/whitespace runs with one underscore, and remove leading/trailing underscores."),
 ("a09_phone_digits","Normalize a phone number","Keep digits only, accept an optional leading country digit 1, and return a ten-digit local number or None."),
 ("a10_query_pairs","Parse URL query pairs","Split ampersand pairs, decode plus as space, retain repeated keys as ordered lists, and ignore malformed pairs."),
 ("a11_slug_text","Build a text slug","Lower-case text, collapse non-alphanumeric runs into one dash, remove boundary dashes, and return an empty string for no alphanumerics."),
 ("a12_range_clamp","Coerce and clamp an integer","Accept integer-like strings or integers, reject booleans/invalid values, and clamp to an inclusive supplied range."),
 ("b01_record_dedup","Deduplicate records by identifier","Return a new list retaining first occurrence order, replace retained values with the last record for an identifier, and do not mutate inputs."),
 ("b02_json_cleanup","Clean JSON-like values recursively","Trim string leaves, drop null dictionary entries, preserve list order, and do not mutate the input structure."),
 ("b03_csv_totals","Aggregate CSV-style rows","Sum valid numeric amount cells by category, ignore malformed rows/cells, and return keys in first-seen category order."),
 ("b04_tag_merge","Merge tag lists","Combine lists in input order, trim/lower-case tags, drop blanks, and preserve the first occurrence of each normalized tag."),
 ("b05_schema_rename","Convert a record schema","Map legacy keys to new keys, trim text fields, supply documented defaults, and ignore unknown keys without mutating input."),
 ("b06_event_filter","Filter timestamped events","Keep mapping events of an allowed type within inclusive ISO-date boundaries and preserve original event order."),
 ("b07_inventory_delta","Reconcile inventory deltas","Apply integer deltas by item, create absent items at zero, reject any result below zero, and return a new mapping."),
 ("b08_contact_group","Group contacts by normalized domain","Extract lower-case domains from valid email strings, skip invalid values, and preserve contact order within each group."),
 ("b09_invoice_cents","Convert invoice amounts to cents","Parse decimal amounts exactly to cents with half-up rounding, skip invalid/negative values, and sum the valid amounts."),
 ("b10_log_summary","Summarize log levels","Count recognized levels case-insensitively, ignore unknown/malformed entries, and return all known levels in fixed order."),
 ("b11_manifest_diff","Compare file manifests","Return added, removed, and changed paths as sorted lists; missing size/hash fields are invalid entries."),
 ("b12_bucket_assign","Assign values to inclusive buckets","Map valid numbers to the first matching inclusive interval, preserve input order, and return None for invalid or unmatched values."),
]

def main() -> None:
    base = ROOT / "tasks" / "s8b"
    if base.exists():
        raise SystemExit("refusing to overwrite existing S8-b task tree")
    for task_id, title, requirement in SPECS:
        target = base / task_id / "template"
        target.mkdir(parents=True)
        (target / "task.md").write_text(f"# Repair `transform`\n\n## {title}\n\nFix `transform` in `solution.py`. {requirement}\n\nKeep the public signature unchanged. Do not modify benchmark-owned verifier files.\n", encoding="utf-8")
        (target / "solution.py").write_text('def transform(value):\n    """Transform a task-specific input value."""\n    return value\n', encoding="utf-8")
    print(f"materialized {len(SPECS)} task templates at {base}")

if __name__ == "__main__":
    main()
