#!/usr/bin/env python3
# scripts/migrate_v2_to_v3.py
# One-shot transform: data/raw/*.json v2 (flat name_th/name_en) → v3 (nested name/prefix)
#   - provinces:   {name_th, name_en} → {name: {th, en}, prefix: null}
#   - districts:   กทม. rows: name_th "เขตพระนคร" → name={th:"พระนคร",...}, prefix={th:"เขต",...}
#                  ต่างจังหวัด: name="เมืองX" เดิม, + prefix={th:"อำเภอ", en:"Amphoe"}
#   - sub_districts: กทม.: + prefix={th:"แขวง", en:"Khwaeng"}
#                    ต่างจังหวัด: + prefix={th:"ตำบล", en:"Tambon"}
# geographies: unchanged (single "name", no locale split)

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw")

BKK_PROVINCE_ID = 1

def load(name):
    with open(os.path.join(RAW, name), "r", encoding="utf-8") as f:
        return json.load(f)

def save(name, data):
    with open(os.path.join(RAW, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def nested(th, en):
    return {"th": th, "en": en}

def pop_legacy_flat(r):
    # Remove any flat columns from a possible earlier migration attempt
    for k in ("name_th", "name_en", "prefix_th", "prefix_en"):
        r.pop(k, None)

def migrate_provinces(rows):
    out = []
    for r in rows:
        name = nested(r.pop("name_th"), r.pop("name_en"))
        pop_legacy_flat(r)
        new = {"id": r["id"], "name": name, "prefix": None}
        new.update({k: v for k, v in r.items() if k != "id"})
        out.append(new)
    return out

def migrate_districts(rows):
    out = []
    for r in rows:
        nm_th = r.pop("name_th")
        nm_en = r.pop("name_en")
        if r["province_id"] == BKK_PROVINCE_ID:
            assert nm_th.startswith("เขต"), f"BKK district missing 'เขต' prefix: id={r['id']} name={nm_th}"
            assert nm_en.startswith("Khet"), f"BKK district missing 'Khet' prefix: id={r['id']} name={nm_en}"
            prefix = nested("เขต", "Khet")
            nm_th = nm_th[len("เขต"):]
            nm_en = nm_en[len("Khet"):].lstrip(" ")
        else:
            prefix = nested("อำเภอ", "Amphoe")
        pop_legacy_flat(r)
        new = {"id": r["id"], "name": nested(nm_th, nm_en), "prefix": prefix}
        new.update({k: v for k, v in r.items() if k != "id"})
        out.append(new)
    return out

def migrate_sub_districts(subs, districts):
    bkk_district_ids = {d["id"] for d in districts if d["province_id"] == BKK_PROVINCE_ID}
    out = []
    for r in subs:
        nm_th = r.pop("name_th")
        nm_en = r.pop("name_en")
        if r["district_id"] in bkk_district_ids:
            prefix = nested("แขวง", "Khwaeng")
        else:
            prefix = nested("ตำบล", "Tambon")
        zip_code = r.pop("zip_code")
        pop_legacy_flat(r)
        new = {"id": r["id"], "zip_code": zip_code, "name": nested(nm_th, nm_en), "prefix": prefix}
        new.update({k: v for k, v in r.items() if k not in ("id", "zip_code")})
        out.append(new)
    return out

def main():
    dry = "--dry-run" in sys.argv
    provs = load("provinces.json")
    dists = load("districts.json")
    subs  = load("sub_districts.json")

    # Detect already-migrated (idempotent guard)
    if dists and "name" in dists[0] and isinstance(dists[0]["name"], dict):
        print("⚠️  data/raw already v3 nested — abort")
        sys.exit(1)

    provs = migrate_provinces(provs)
    dists = migrate_districts(dists)
    subs  = migrate_sub_districts(subs, dists)

    sample_bkk = next(d for d in dists if d["id"] == 1001)
    sample_bkk_sub = next(s for s in subs if s["district_id"] == 1001)
    sample_prov = next(d for d in dists if d["id"] == 1101)
    sample_province_row = next(p for p in provs if p["id"] == 1)
    print(f"Province sample: {sample_province_row}")
    print(f"BKK district:    {sample_bkk}")
    print(f"BKK sub_district:{sample_bkk_sub}")
    print(f"Prov district:   {sample_prov}")
    print(f"counts: provs={len(provs)}, dists={len(dists)}, subs={len(subs)}")

    if dry:
        print("⚠️  dry-run, no file written")
        return

    save("provinces.json", provs)
    save("districts.json", dists)
    save("sub_districts.json", subs)
    print("✅ v3 nested migration applied to data/raw/*.json")

if __name__ == "__main__":
    main()
