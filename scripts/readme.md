# Scripts

Pipeline: `data/raw/` + `data/spec/` → `formats/` + `api/latest/`
รันทั้ง pipeline: **`docker compose run --rm make`** (recommended, no local setup)
หรือ `python3 scripts/make.py` (local Python — ต้องมี `pandas` + `openpyxl`)

| script | ทำอะไร | flags |
|---|---|---|
| `0_validate_data.py` | validate raw ตาม spec (schema, FK, unique id, zip_code/lat/long); exit 1 เมื่อ error | `--strict`, `--fail-on-warn` |
| `1_export_file_format.py` | emit `formats/{csv,json,sql,xlsx,xml}/<table>.<ext>` — JSON/XML เก็บ nested; CSV/SQL/XLSX flatten → `name_th`/`prefix_th`/… | `--overwrite`, `--no-create` (ข้าม SQL DDL). ต้อง pandas+openpyxl สำหรับ XLSX (ไม่มี = warn + skip) |
| `2_export_api.py` | emit nested API JSON 5 ไฟล์ใน `api/latest/` (province/district/sub_district + 2 combined) | `--overwrite` |
| `make.py` | orchestrator — รัน 0 → 1 → 2, หยุดถ้า step ไหน fail | — |
| `migrate_v2_to_v3.py` | one-shot: transform `data/raw/` v2 flat → v3 nested; idempotent guard (ข้ามถ้า already nested) | `--dry-run` |

ดู env setup, Docker, PR workflow → [CONTRIBUTING.md](../CONTRIBUTING.md)
ทุก script รองรับ `--help`, `--root` (override repo root)
