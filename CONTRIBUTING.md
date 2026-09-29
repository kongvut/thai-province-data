# Contributing Guide

ขอบคุณที่สนใจร่วมพัฒนา **thai-province-data** — ชุดข้อมูลจังหวัด / อำเภอ / ตำบล ของประเทศไทย

ไทย | [English](CONTRIBUTING.en.md)

ข้อมูลใน repo นี้เป็น **open data** ที่รวมจากหลายแหล่ง (กรมการปกครอง, ไปรษณีย์ไทย) — ทุก PR ต้องมี **reference** ที่ชัดเจนเพื่อความถูกต้องระยะยาว

---

## Workflow

1. **Fork** repo ไปยังบัญชี GitHub ของคุณ
2. **Branch ใหม่** จาก `master`:
   ```bash
   git checkout -b fix-bueng-kan-zip
   ```
   ชื่อที่แนะนำ: `fix-<entity>-<short-issue>` หรือ `add-<new-entity>` (เช่น `add-district-kanlapaphruek`, `update-sub-district-spelling`)
3. **แก้ที่ `data/raw/*.json` เท่านั้น** (พร้อมอัปเดต `updated_at` ของแถวที่แก้) — `formats/` และ `api/latest/` เป็น artifact regenerated อัตโนมัติ
4. **Validate + regen**:
   ```bash
   python3 scripts/make.py
   ```
   (หรือ `docker compose run --rm make` — ดู [Docker](#docker-ไม่ต้องติดตั้ง-python-dependencies-เอง))
5. **Commit** — ใช้ conventional commit สั้น ๆ เช่น:
   - `fix(data): correct zip code for sub_district 102601`
   - `add(data): new district กัลยาณิวัฒนา in Chiang Mai`
   - `docs: update API URL list in README`
6. **เปิด PR** มายัง branch `master` — ใส่รายละเอียดตาม template ด้านล่าง

---

## Data rules (v3 schema)

Source of truth: [`data/spec/*.json`](data/spec/) — schema เปลี่ยนคือ breaking change ต้อง Discuss ผ่าน issue ก่อน

| Entity | field | ต้องมี? | ตัวอย่าง |
|---|---|---|---|
| district | `name.th` / `name.en` | ✅ base name เท่านั้น | `"พระนคร"` / `"Phra Nakhon"` |
| district | `prefix.th` / `prefix.en` | ✅ **ห้าม null** | กทม. = `"เขต"`/`"Khet"`, ต่างจังหวัด = `"อำเภอ"`/`"Amphoe"` |
| sub_district | `prefix.th` / `prefix.en` | ✅ **ห้าม null** | กทม. = `"แขวง"`/`"Khwaeng"`, ต่างจังหวัด = `"ตำบล"`/`"Tambon"` |
| province | `prefix` | ต้องมี key = `null` | (จังหวัดไม่มี convention prefix) |
| ทุก entity | `id` | primary key, ห้ามซ้ำ, ห้ามเปลี่ยนค่า id เก่า | |

**ข้อห้ามสำคัญ:**
- ❌ `name.th` ต้อง **ไม่มี** prefix ติดมา — `"เขตพระนคร"` ผิด → แยกเป็น `name.th: "พระนคร"`, `prefix.th: "เขต"`
- ❌ `name_th`/`name_en`/`prefix_th`/`prefix_en` (flat columns) — v2 schema, ห้ามใส่กลับ
- ❌ แก้ชื่อคอลัมน์/keys ใน `data/spec/*.json` โดยไม่มี issue อภิปราย
- ❌ แก้ `api/v1/`, `api/v2/`, `formats-v2/` (frozen legacy snapshots)
- ❌ `district_id` ของ sub_district ใหม่ต้อง FK valid → validate script จะตรวจ

**Edge case — เมือง capitals:**
`name.th = "เมืองสมุทรปราการ"` (district id 1101) เป็นชื่อเต็มของอำเภอเมืองจังหวัด — "เมือง" เป็นส่วนหนึ่งของ **name** ไม่ใช่ prefix ที่ต้อง strip → `prefix.th = "อำเภอ"`, `name.th = "เมืองสมุทรปราการ"`

---

## PR body template

```markdown
## Pull Request: <สรุป 1 บรรทัด>
Closes #<issue>

### Summary
<อธิบาย: เปลี่ยนอะไร ทำไม>

### Changes
- `data/raw/districts.json` — เพิ่มอำเภอ กัลยาณิวัฒนา (id 5025)
- `data/raw/sub_districts.json` — ย้าย 3 ตำบลจาก อำเภอแม่แจ่ม → กัลยาณิวัฒนา

### Reference
- <URL ทางการ — กรมการปกครอง / ราชกิจจานุเบกษา / วิกิพีไทย (มี citation)>

### Impact
- [ ] API endpoint (`api/latest/`) affected (regen ด้วย make.py แล้ว)
- [ ] Format exports affected (regen แล้ว)
- [ ] Breaking schema change (ต้อง discuss ใน issue ก่อน)
```

**ตัวอย่างจริง:** [PR #34](https://github.com/kongvut/thai-province-data/pull/34) — add new district, [PR #46](https://github.com/kongvut/thai-province-data/pull/46) — bulk restore from DOPA + Bueng Kan renumbering

---

## Review criteria

Maintainer ตรวจ PR ทุกตัวตามนี้:

- ✅ **validate ผ่าน**: `python3 scripts/0_validate_data.py --strict --fail-on-warn`
- ✅ **regen ผ่าน**: `python3 scripts/make.py` → formats + api/latest ต้อง match commit
- ✅ **reference ชัด**: ทุกข้อมูลใหม่/แก้ต้องมีแหล่งอ้างอิง
- ✅ **prefix ถูกประเภท**: ตรวจด้วยตา 1 ครั้ง — กทม. vs ต่างจังหวัดสลับกันบ่อย
- ✅ **CI workflow** (validate-raw.yml) = green

PR ที่มี schema change (field add/rename) ต้อง discuss เป็น issue ก่อน แล้วค่อยส่ง PR

---

## ติดตั้ง environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pandas openpyxl
```

(`pandas` + `openpyxl` จำเป็นสำหรับ export `.xlsx`; script ตัวอื่นใช้ stdlib)

## Pipeline

รันทั้ง pipeline (validate → export formats → export api) ทีละคำสั่งเดียว:

```bash
python3 scripts/make.py
```

หรือทีละ step:

```bash
python3 scripts/0_validate_data.py --strict --fail-on-warn     # schema + FK + invariants
python3 scripts/1_export_file_format.py --overwrite            # CSV/SQL/XLSX/JSON/XML
python3 scripts/2_export_api.py --overwrite                    # api/latest/*.json
```

ถ้า validate fail → make.py หยุดทันที, exit code 1 (CI ก็ fail เช่นกัน)

## Docker (ไม่ต้องติดตั้ง Python/dependencies เอง)

```bash
docker compose build                    # ติดตั้ง pandas + openpyxl ภายใน container
docker compose run --rm validate        # รัน validator อย่างเดียว (strict + fail-on-warn)
docker compose run --rm make            # รัน pipeline เต็ม
```

volume mount `./:/app:rw` — แก้ไขไฟล์ใน repo บน host ได้เลย, container เห็นผลทันที

## License

ทุก contribution ที่ merge เข้า repo นี้ถือเป็น MIT License (ดู [LICENSE](LICENSE))
