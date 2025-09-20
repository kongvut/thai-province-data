#!/usr/bin/env python3
# scripts/0_validate_data.py
# Validate thai-province-data v2 using JSON specs in data/spec and inputs from data/raw

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------
# Paths (relative to repo root)
# ---------------------------
SPEC_DIR = "data/spec"
RAW_DIR = "data/raw"

SPECS = {
    "geography": os.path.join(SPEC_DIR, "geography.json"),
    "province": os.path.join(SPEC_DIR, "province.json"),
    "district": os.path.join(SPEC_DIR, "district.json"),
    "sub_district": os.path.join(SPEC_DIR, "sub_district.json"),
}

RAW = {
    "geographies": os.path.join(RAW_DIR, "geographies.json"),
    "provinces": os.path.join(RAW_DIR, "provinces.json"),
    "districts": os.path.join(RAW_DIR, "districts.json"),
    "sub_districts": os.path.join(RAW_DIR, "sub_districts.json"),
}

# ---------------------------
# Utilities
# ---------------------------

class Issues:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def err(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def summarize(self, fail_on_warn: bool) -> int:
        if self.errors:
            print("\n❌ Errors:")
            for e in self.errors:
                print(f"  - {e}")
        if self.warnings:
            print("\n⚠️  Warnings:")
            for w in self.warnings:
                print(f"  - {w}")
        if self.errors:
            return 1
        if fail_on_warn and self.warnings:
            return 1
        return 0

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_integer(v: Any) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return True
    if isinstance(v, str) and v.strip().isdigit():
        return True
    return False

def to_int(v: Any) -> Optional[int]:
    if is_integer(v):
        try:
            return int(v)
        except Exception:
            return None
    return None

def is_number(v: Any) -> bool:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return True
    # allow string that looks like number
    if isinstance(v, str):
        try:
            float(v.strip())
            return True
        except Exception:
            return False
    return False

def to_number(v: Any) -> Optional[float]:
    if is_number(v):
        try:
            return float(v)
        except Exception:
            return None
    return None

def is_string(v: Any) -> bool:
    return isinstance(v, str)

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def parse_iso8601(s: str) -> bool:
    """Accepts ISO8601 with timezone, including 'Z'."""
    try:
        # Python accepts "+07:00" with fromisoformat in 3.11+
        # Replace trailing 'Z' to '+00:00' for compatibility
        s2 = s.replace("Z", "+00:00")
        datetime.fromisoformat(s2)
        return True
    except Exception:
        return False

POSTAL_RE = re.compile(r"^\d{5}$")

# ---------------------------
# Minimal JSON Schema validator (subset)
# Supports: type, maxLength, required, format: date-time, nullable via ["string","null"]
# ---------------------------

def validate_against_schema(obj: Dict[str, Any], schema: Dict[str, Any], issues: Issues, ctx: str, strict: bool):
    # required
    required = schema.get("required", [])
    for k in required:
        if k not in obj:
            issues.err(f"{ctx}: missing required key '{k}'")
    props: Dict[str, Any] = schema.get("properties", {})

    # check unknown keys? (warn only)
    for k in obj.keys():
        if k not in props:
            # allow additional props silently, but warn
            issues.warn(f"{ctx}: unknown key '{k}' not in spec")

    for key, prop in props.items():
        if key not in obj:
            continue
        val = obj[key]
        # handle type(s)
        typ = prop.get("type")
        types = typ if isinstance(typ, list) else [typ] if typ else []
        # nullability
        if val is None:
            if "null" in types or not types:
                continue
            else:
                issues.err(f"{ctx}: key '{key}' is null but spec type disallows null")
                continue

        # type checks
        if "integer" in types:
            if not is_integer(val):
                issues.err(f"{ctx}: key '{key}' should be integer")
        elif "number" in types:
            if not is_number(val):
                issues.err(f"{ctx}: key '{key}' should be number")
        elif "string" in types:
            if not is_string(val):
                issues.err(f"{ctx}: key '{key}' should be string")
            else:
                maxlen = prop.get("maxLength")
                if isinstance(maxlen, int) and len(val) > maxlen:
                    issues.err(f"{ctx}: key '{key}' exceeds maxLength {maxlen}")
                # basic leading/trailing whitespace check
                if val != val.strip():
                    issues.warn(f"{ctx}: key '{key}' has leading/trailing spaces")
                # format checks
                fmt = prop.get("format")
                if fmt == "date-time":
                    if not parse_iso8601(val):
                        issues.err(f"{ctx}: key '{key}' not valid ISO8601 date-time")
        elif types and types != ["null"]:
            # some other type not implemented
            issues.warn(f"{ctx}: key '{key}' type '{types}' not fully validated by lightweight validator")

        # extra simple constraints
        if prop.get("enum"):
            if val not in prop["enum"]:
                issues.err(f"{ctx}: key '{key}' not in enum {prop['enum']}")

# ---------------------------
# Domain validations
# ---------------------------

def validate_unique_ids(name: str, rows: List[Dict[str, Any]], issues: Issues):
    seen = set()
    dups = []
    for i, r in enumerate(rows, 1):
        rid = to_int(r.get("id"))
        if rid is None:
            issues.err(f"[{name}] row {i}: missing/invalid id")
            continue
        if rid in seen:
            dups.append((i, rid))
        seen.add(rid)
    if dups:
        ids = sorted(set(r for _, r in dups))
        issues.err(f"[{name}] duplicate id(s): {ids}")

def fk_check(child_rows: List[Dict[str, Any]], child_label: str,
             fk_col: str, parent_index: Dict[int, Dict[str, Any]],
             parent_label: str, issues: Issues):
    for i, r in enumerate(child_rows, 1):
        fk = to_int(r.get(fk_col))
        if fk is None:
            issues.err(f"[{child_label}] row {i}: {fk_col} missing/invalid")
            continue
        if fk not in parent_index:
            issues.err(f"[{child_label}] row {i}: {fk_col}={fk} not found in {parent_label}.id")

def index_by_id(rows: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    idx = {}
    for r in rows:
        rid = to_int(r.get("id"))
        if rid is not None:
            idx[rid] = r
    return idx

def validate_zip_lat_long(sub_rows: List[Dict[str, Any]], issues: Issues):
    for i, r in enumerate(sub_rows, 1):
        # zip_code
        zip_code = r.get("zip_code")
        if zip_code is None:
            issues.err(f"[sub_districts] row {i}: zip_code missing")
        else:
            z = str(zip_code).strip()
            if not POSTAL_RE.match(z):
                issues.err(f"[sub_districts] row {i}: invalid zip_code '{zip_code}' (expect 5 digits)")

        # lat/long if present
        lat = r.get("lat")
        lon = r.get("long")
        if lat is not None:
            latf = to_number(lat)
            if latf is None or not (-90.0 <= latf <= 90.0):
                issues.err(f"[sub_districts] row {i}: invalid lat '{lat}'")
        if lon is not None:
            lonf = to_number(lon)
            if lonf is None or not (-180.0 <= lonf <= 180.0):
                issues.err(f"[sub_districts] row {i}: invalid long '{lon}'")

# ---------------------------
# Main
# ---------------------------

def main():
    parser = argparse.ArgumentParser(description="Validate v2 raw data using JSON specs")
    parser.add_argument("--root", default=None, help="Repo root (default: auto detect)")
    parser.add_argument("--fail-on-warn", action="store_true", help="Exit non-zero on warnings")
    parser.add_argument("--strict", action="store_true", help="Stricter schema checks (if applicable)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = args.root or os.path.abspath(os.path.join(script_dir, ".."))
    print(f"📁 Repo root: {repo_root}")

    issues = Issues()

    # Load specs
    specs: Dict[str, Dict[str, Any]] = {}
    for key, rel in SPECS.items():
        path = os.path.join(repo_root, rel)
        if not os.path.exists(path):
            issues.err(f"Spec not found: {rel}")
            continue
        try:
            specs[key] = load_json(path)
        except Exception as e:
            issues.err(f"Spec parse error: {rel} ({e})")

    # Load raw arrays
    raws: Dict[str, List[Dict[str, Any]]] = {}
    for key, rel in RAW.items():
        path = os.path.join(repo_root, rel)
        if not os.path.exists(path):
            issues.err(f"Raw data not found: {rel}")
            raws[key] = []
            continue
        try:
            data = load_json(path)
            if not isinstance(data, list):
                issues.err(f"Raw {rel} must be a JSON array")
                raws[key] = []
            else:
                raws[key] = data
        except Exception as e:
            issues.err(f"Raw parse error: {rel} ({e})")
            raws[key] = []

    # Early stop if critical loads failed
    if issues.errors:
        exit_code = issues.summarize(args.fail_on_warn)
        sys.exit(exit_code)

    # Validate by schema
    pairs = [
        ("geographies", "geography"),
        ("provinces", "province"),
        ("districts", "district"),
        ("sub_districts", "sub_district"),
    ]

    for raw_name, spec_name in pairs:
        rows = raws.get(raw_name, [])
        spec = specs.get(spec_name, {})
        print(f"• Validating {raw_name}: {len(rows)} rows against spec '{spec_name}'")
        if not spec:
            issues.err(f"Missing spec object for '{spec_name}'")
            continue
        for i, obj in enumerate(rows, 1):
            ctx = f"[{raw_name}] row {i}"
            if not isinstance(obj, dict):
                issues.err(f"{ctx}: item must be object/dict")
                continue
            validate_against_schema(obj, spec, issues, ctx, args.strict)

        # Primary-key uniqueness for id
        validate_unique_ids(raw_name, rows, issues)

    # Foreign keys
    geogs = raws["geographies"]
    provs = raws["provinces"]
    dists = raws["districts"]
    subs  = raws["sub_districts"]

    geog_idx = index_by_id(geogs)
    prov_idx = index_by_id(provs)
    dist_idx = index_by_id(dists)

    # provinces.geography_id → geographies.id
    fk_check(provs, "provinces", "geography_id", geog_idx, "geographies", issues)
    # districts.province_id → provinces.id
    fk_check(dists, "districts", "province_id", prov_idx, "provinces", issues)
    # sub_districts.district_id → districts.id
    fk_check(subs, "sub_districts", "district_id", dist_idx, "districts", issues)

    # Postal & lat/long
    validate_zip_lat_long(subs, issues)

    # Soft name checks (trim spaces)
    def soft_name_trim_check(label: str, rows: List[Dict[str, Any]], keys: List[str]):
        for i, r in enumerate(rows, 1):
            for k in keys:
                if k in r and isinstance(r[k], str) and r[k] != r[k].strip():
                    issues.warn(f"[{label}] row {i}: '{k}' has leading/trailing spaces")
    soft_name_trim_check("provinces", provs, ["name_th", "name_en"])
    soft_name_trim_check("districts", dists, ["name_th", "name_en"])
    soft_name_trim_check("sub_districts", subs, ["name_th", "name_en"])
    soft_name_trim_check("geographies", geogs, ["name"])

    # Summary
    print("\n✅ Validation finished.")
    exit_code = issues.summarize(args.fail_on_warn)
    if exit_code == 0:
        print("\n🎉 All good.")
    else:
        print("\n⛔ Validation failed.")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
