#!/usr/bin/env python3
# scripts/1_export_file_format.py
# Export data/raw/*.json to formats/{csv,json,sql,xlsx,xml}

import argparse
import csv
import json
import os
import sys
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

# ---------------------------
# Optional deps for XLSX
# ---------------------------
HAS_PANDAS = True
try:
    import pandas as pd
except Exception:
    HAS_PANDAS = False

# ---------------------------
# Paths
# ---------------------------
RAW_DIR = "data/raw"
SPEC_DIR = "data/spec"
OUT_DIRS = {
    "csv": "formats/csv",
    "json": "formats/json",
    "sql": "formats/sql",
    "xlsx": "formats/xlsx",
    "xml": "formats/xml",
}

RAW_FILES = {
    "geographies": os.path.join(RAW_DIR, "geographies.json"),
    "provinces": os.path.join(RAW_DIR, "provinces.json"),
    "districts": os.path.join(RAW_DIR, "districts.json"),
    "sub_districts": os.path.join(RAW_DIR, "sub_districts.json"),
}

SPEC_FILES = {
    "geography": os.path.join(SPEC_DIR, "geography.json"),
    "province": os.path.join(SPEC_DIR, "province.json"),
    "district": os.path.join(SPEC_DIR, "district.json"),
    "sub_district": os.path.join(SPEC_DIR, "sub_district.json"),
}

# ---------------------------
# Output file mapping and canonical column order
# (order from SQL schema provided)
# ---------------------------
COLUMN_ORDER = {
    "geographies": ["id", "name"],
    "provinces": ["id", "name_th", "name_en", "geography_id", "created_at", "updated_at", "deleted_at"],
    "districts": ["id", "name_th", "name_en", "province_id", "created_at", "updated_at", "deleted_at"],
    "sub_districts": ["id", "zip_code", "name_th", "name_en", "district_id", "lat", "long", "created_at", "updated_at", "deleted_at"],
}

# ---------------------------
# SQL DDL (from user-provided schema)
# ---------------------------
DDL = {
    "geographies": """CREATE TABLE `geographies` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",
    "provinces": """CREATE TABLE `provinces` (
  `id` int(11) NOT NULL,
  `name_th` varchar(150) NOT NULL,
  `name_en` varchar(150) NOT NULL,
  `geography_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",
    "districts": """CREATE TABLE `districts` (
  `id` int(11) NOT NULL,
  `name_th` varchar(150) NOT NULL,
  `name_en` varchar(150) NOT NULL,
  `province_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",
    "sub_districts": """CREATE TABLE `sub_districts` (
  `id` int(11) NOT NULL,
  `zip_code` int(11) NOT NULL,
  `name_th` varchar(150) NOT NULL,
  `name_en` varchar(150) NOT NULL,
  `district_id` int(11) NOT NULL,
  `lat` double DEFAULT NULL,
  `long` double DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"""
}

# ---------------------------
# Helpers
# ---------------------------

def ensure_dirs(root: str):
    for d in OUT_DIRS.values():
        outdir = os.path.join(root, d)
        os.makedirs(outdir, exist_ok=True)

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data: Any, indent: int):
    with open(path, "w", encoding="utf-8") as f:
        if indent and indent > 0:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        else:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

def sql_escape(value: Any) -> str:
    """Return SQL literal for MySQL dialect."""
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        # integers/floats as-is
        return str(value)
    # strings or others
    s = str(value)
    s = s.replace("'", "''")  # escape single quotes
    return f"'{s}'"

def to_rows_in_order(rows: List[Dict[str, Any]], order: List[str]) -> List[List[Any]]:
    out = []
    for r in rows:
        out.append([r.get(col, None) for col in order])
    return out

def write_csv(path: str, headers: List[str], rows2d: List[List[Any]]):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows2d:
            writer.writerow([("" if v is None else v) for v in row])

def write_sql(path: str, table: str, headers: List[str], rows2d: List[List[Any]], include_create: bool):
    with open(path, "w", encoding="utf-8") as f:
        if include_create:
            f.write(DDL[table].rstrip() + "\n\n")
        if not rows2d:
            return
        # batch inserts for readability
        f.write(f"INSERT INTO `{table}` ({', '.join('`'+h+'`' for h in headers)}) VALUES\n")
        lines = []
        for row in rows2d:
            vals = ", ".join(sql_escape(v) for v in row)
            lines.append(f"  ({vals})")
        f.write(",\n".join(lines))
        f.write(";\n")

def write_xlsx(path: str, headers: List[str], rows2d: List[List[Any]]):
    if not HAS_PANDAS:
        print(f"⚠️  pandas/openpyxl not available; skip XLSX: {os.path.basename(path)}")
        return
    df = pd.DataFrame(rows2d, columns=headers)
    # pandas will handle datatypes and None -> NaN as needed
    df.to_excel(path, index=False)

def dict_to_xml(tag: str, d: Dict[str, Any]) -> Element:
    """Convert dict to XML element <tag> with simple child elements."""
    e = Element(tag)
    for k, v in d.items():
        child = SubElement(e, k)
        child.text = "" if v is None else str(v)
    return e

def write_xml(path: str, root_tag: str, item_tag: str, rows: List[Dict[str, Any]]):
    root = Element(root_tag)
    for r in rows:
        node = dict_to_xml(item_tag, r)
        root.append(node)
    tree = ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)

def load_spec_columns(repo_root: str, spec_file: str) -> List[str]:
    """Try to read properties order from spec. If not reliable, fall back to COLUMN_ORDER."""
    path = os.path.join(repo_root, spec_file)
    try:
        spec = load_json(path)
        props = spec.get("properties", {})
        # JSON object has no guaranteed order, so we will
        # use COLUMN_ORDER defined above for canonical order.
        return []  # signal to use COLUMN_ORDER
    except Exception:
        return []

# ---------------------------
# Main export
# ---------------------------

def export_table(repo_root: str, table: str, raw_name: str, json_indent: int, overwrite: bool, include_create: bool):
    raw_path = os.path.join(repo_root, RAW_FILES[raw_name])
    if not os.path.exists(raw_path):
        print(f"⛔ Missing: {RAW_FILES[raw_name]}")
        return

    rows = load_json(raw_path)
    if not isinstance(rows, list):
        print(f"⛔ {RAW_FILES[raw_name]} must be a JSON array")
        return

    # column order
    order = COLUMN_ORDER[table]
    rows2d = to_rows_in_order(rows, order)

    # ensure out dirs
    for ext, d in OUT_DIRS.items():
        os.makedirs(os.path.join(repo_root, d), exist_ok=True)

    # file paths
    csv_path  = os.path.join(repo_root, OUT_DIRS["csv"],  f"{table}.csv")
    json_path = os.path.join(repo_root, OUT_DIRS["json"], f"{table}.json")
    sql_path  = os.path.join(repo_root, OUT_DIRS["sql"],  f"{table}.sql")
    xlsx_path = os.path.join(repo_root, OUT_DIRS["xlsx"], f"{table}.xlsx")
    xml_path  = os.path.join(repo_root, OUT_DIRS["xml"],  f"{table}.xml")

    # overwrite guard
    for p in [csv_path, json_path, sql_path, xlsx_path, xml_path]:
        if (not overwrite) and os.path.exists(p):
            print(f"⚠️  Exists (skip). Use --overwrite to replace: {os.path.relpath(p, repo_root)}")

    # CSV
    if overwrite or not os.path.exists(csv_path):
        write_csv(csv_path, order, rows2d)
        print(f"✅ CSV   -> {os.path.relpath(csv_path, repo_root)}")

    # JSON (array)
    if overwrite or not os.path.exists(json_path):
        save_json(json_path, rows, json_indent)
        print(f"✅ JSON  -> {os.path.relpath(json_path, repo_root)}")

    # SQL
    if overwrite or not os.path.exists(sql_path):
        write_sql(sql_path, table, order, rows2d, include_create)
        print(f"✅ SQL   -> {os.path.relpath(sql_path, repo_root)}")

    # XLSX
    if overwrite or not os.path.exists(xlsx_path):
        write_xlsx(xlsx_path, order, rows2d)
        if HAS_PANDAS:
            print(f"✅ XLSX  -> {os.path.relpath(xlsx_path, repo_root)}")

    # XML
    if overwrite or not os.path.exists(xml_path):
        # root tags
        root_tag = table  # e.g., "provinces"
        item_tag = {
            "geographies": "geography",
            "provinces": "province",
            "districts": "district",
            "sub_districts": "sub_district"
        }[table]
        write_xml(xml_path, root_tag, item_tag, rows)
        print(f"✅ XML   -> {os.path.relpath(xml_path, repo_root)}")

def main():
    parser = argparse.ArgumentParser(description="Export data/raw/*.json to formats/{csv,json,sql,xlsx,xml}")
    parser.add_argument("--root", default=None, help="Repo root (default: auto)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent (0 or None for compact)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--no-create", action="store_true", help="Do not include CREATE TABLE in SQL output")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = args.root or os.path.abspath(os.path.join(script_dir, ".."))

    ensure_dirs(repo_root)

    if not HAS_PANDAS:
        print("⚠️  pandas/openpyxl not detected; XLSX export will be skipped.")

    include_create = not args.no_create

    # Export each table
    export_table(repo_root, "geographies",   "geographies",   args.indent, args.overwrite, include_create)
    export_table(repo_root, "provinces",     "provinces",     args.indent, args.overwrite, include_create)
    export_table(repo_root, "districts",     "districts",     args.indent, args.overwrite, include_create)
    export_table(repo_root, "sub_districts", "sub_districts", args.indent, args.overwrite, include_create)

    print("🏁 Done.")

if __name__ == "__main__":
    main()
