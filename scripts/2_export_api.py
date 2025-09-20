#!/usr/bin/env python3
# scripts/2_export_api.py
# Build API JSON from data/raw into api/latest

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

RAW_DIR = "data/raw"
OUT_DIR = "api/latest"

RAW_FILES = {
    "provinces": os.path.join(RAW_DIR, "provinces.json"),
    "districts": os.path.join(RAW_DIR, "districts.json"),
    "sub_districts": os.path.join(RAW_DIR, "sub_districts.json"),
}

# Desired key orders for prettier, consistent JSON outputs
ORDER_PROVINCE = [
    "id", "name_th", "name_en", "geography_id", "created_at", "updated_at", "deleted_at"
]
ORDER_DISTRICT = [
    "id", "name_th", "name_en", "province_id", "created_at", "updated_at", "deleted_at"
]
ORDER_SUB_DISTRICT = [
    "id", "zip_code", "name_th", "name_en", "district_id", "lat", "long",
    "created_at", "updated_at", "deleted_at"
]

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data: Any, indent: int, overwrite: bool):
    if (not overwrite) and os.path.exists(path):
        print(f"⚠️  Exists (skip) {path}. Use --overwrite to replace.")
        return
    with open(path, "w", encoding="utf-8") as f:
        if indent and indent > 0:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        else:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"✅ Wrote {os.path.relpath(path)}")

def order_keys(d: Dict[str, Any], order: List[str]) -> Dict[str, Any]:
    """Return a new dict with keys in desired order; unknown keys appended at the end."""
    out = {}
    for k in order:
        if k in d:
            out[k] = d[k]
    for k, v in d.items():
        if k not in out:
            out[k] = v
    return out

def index_by_id(rows: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    idx = {}
    for r in rows:
        rid = r.get("id")
        if isinstance(rid, int):
            idx[rid] = r
    return idx

def build_province_with_children(
        provinces: List[Dict[str, Any]],
        districts: List[Dict[str, Any]],
        sub_districts: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    # group districts by province_id
    dist_by_pid: Dict[int, List[Dict[str, Any]]] = {}
    for d in districts:
        pid = d.get("province_id")
        if isinstance(pid, int):
            dist_by_pid.setdefault(pid, []).append(d)

    # group sub_districts by district_id
    sub_by_did: Dict[int, List[Dict[str, Any]]] = {}
    for s in sub_districts:
        did = s.get("district_id")
        if isinstance(did, int):
            sub_by_did.setdefault(did, []).append(s)

    result: List[Dict[str, Any]] = []
    for p in provinces:
        # clone province with field order
        p_clone = order_keys(dict(p), ORDER_PROVINCE)
        # attach districts
        dlist_out: List[Dict[str, Any]] = []
        for d in dist_by_pid.get(p.get("id"), []) or []:
            d_clone = order_keys(dict(d), ORDER_DISTRICT)
            # attach sub_districts
            s_list_out: List[Dict[str, Any]] = []
            for s in sub_by_did.get(d.get("id"), []) or []:
                s_clone = order_keys(dict(s), ORDER_SUB_DISTRICT)
                s_list_out.append(s_clone)
            d_clone["sub_districts"] = s_list_out
            dlist_out.append(d_clone)
        p_clone["districts"] = dlist_out
        result.append(p_clone)
    return result

def build_sub_district_with_parents(
        sub_districts: List[Dict[str, Any]],
        districts: List[Dict[str, Any]],
        provinces: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    dist_idx = index_by_id(districts)
    prov_idx = index_by_id(provinces)

    out: List[Dict[str, Any]] = []
    for s in sub_districts:
        s_clone = order_keys(dict(s), ORDER_SUB_DISTRICT)

        did = s.get("district_id")
        d_obj: Optional[Dict[str, Any]] = None
        if isinstance(did, int) and did in dist_idx:
            d_src = dist_idx[did]
            d_clone = order_keys(dict(d_src), ORDER_DISTRICT)

            pid = d_src.get("province_id")
            if isinstance(pid, int) and pid in prov_idx:
                p_src = prov_idx[pid]
                p_clone = order_keys(dict(p_src), ORDER_PROVINCE)
                d_clone["province"] = p_clone
            else:
                print(f"⚠️  Missing province for district_id={did} (province_id={pid}) — skip embedding province.")

            d_obj = d_clone
        else:
            print(f"⚠️  Missing district for sub_district_id={s.get('id')} (district_id={did}) — skip embedding district.")
        if d_obj is not None:
            s_clone["district"] = d_obj

        out.append(s_clone)
    return out

def main():
    parser = argparse.ArgumentParser(description="Export API JSON to api/latest from data/raw")
    parser.add_argument("--root", default=None, help="Repo root (default: auto)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent spaces (0 for compact)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing api files")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = args.root or os.path.abspath(os.path.join(script_dir, ".."))

    out_dir = os.path.join(repo_root, OUT_DIR)
    ensure_dir(out_dir)

    # Load raw data
    try:
        provinces = load_json(os.path.join(repo_root, RAW_FILES["provinces"]))
        districts = load_json(os.path.join(repo_root, RAW_FILES["districts"]))
        sub_districts = load_json(os.path.join(repo_root, RAW_FILES["sub_districts"]))
    except FileNotFoundError as e:
        print(f"⛔ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"⛔ Failed to read inputs: {e}")
        sys.exit(1)

    # Sanity: ensure arrays
    for name, arr in [("provinces", provinces), ("districts", districts), ("sub_districts", sub_districts)]:
        if not isinstance(arr, list):
            print(f"⛔ {name} must be a JSON array")
            sys.exit(1)

    # Flat files (as-is but ordered keys)
    provinces_out = [order_keys(dict(p), ORDER_PROVINCE) for p in provinces]
    districts_out = [order_keys(dict(d), ORDER_DISTRICT) for d in districts]
    sub_districts_out = [order_keys(dict(s), ORDER_SUB_DISTRICT) for s in sub_districts]

    save_json(os.path.join(out_dir, "province.json"), provinces_out, args.indent, args.overwrite)
    save_json(os.path.join(out_dir, "district.json"), districts_out, args.indent, args.overwrite)
    save_json(os.path.join(out_dir, "sub_district.json"), sub_districts_out, args.indent, args.overwrite)

    # Nested: province -> districts -> sub_districts
    nested_prov = build_province_with_children(provinces, districts, sub_districts)
    save_json(
        os.path.join(out_dir, "province_with_district_and_sub_district.json"),
        nested_prov, args.indent, args.overwrite
    )

    # Nested: sub_district -> district -> province
    nested_sub = build_sub_district_with_parents(sub_districts, districts, provinces)
    save_json(
        os.path.join(out_dir, "sub_district_with_district_and_province.json"),
        nested_sub, args.indent, args.overwrite
    )

    print("🏁 Done.")

if __name__ == "__main__":
    main()
