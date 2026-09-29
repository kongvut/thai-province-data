# Changelog

## [3.1.0] - 2026-09-29

### Changed (⚠️ breaking สำหรับ geography consumers)
- **Geography** `name` จาก string → nested object `{th, en}` ให้สอดคล้องกับ entity อื่นใน v3
  - ก่อน: `{"id": 1, "name": "ภาคเหนือ"}`
  - หลัง: `{"id": 1, "name": {"th": "ภาคเหนือ", "en": "Northern"}}`
  - English names (adjective form): Northern, Central, Northeastern, Western, Eastern, Southern
  - geography ไม่มี concept ของ prefix → **ไม่มี** `prefix` field (ต่างจาก province ที่ `prefix: null`)
- `formats/{csv,sql,xlsx}/geographies` flatten เป็น `name_th`, `name_en` columns; JSON/XML เก็บ nested ตาม source
- `data/spec/geography.json` — `name` type `string` → `object {th, en}`
- SQL DDL `geographies.name` → `geographies.name_th` + `geographies.name_en` (VARCHAR(255))

### Notes
- ไม่มีผลต่อ `api/latest/` — geography ไม่ได้ถูก export เป็น API file (มีแค่ `province.geography_id` แบบ int ซึ่งไม่เปลี่ยน)
- เป็น consistency fix ปิดท้าย v3 (v3.0.0 ปล่อย geography เป็น flat string ไว้ก่อน)
- **Consumer ที่ยังต้องใช้ `formats/csv/geographies.csv` แบบ column เดิม** (`id,name`): ใช้ [`formats-v2/csv/geographies.csv`](formats-v2/csv/geographies.csv) — snapshot v2 เก็บ shape เดิมไว้ และ shape นี้เหมือนกันทุกประการระหว่าง v2 กับ v3.0.0 (ยังไม่ถูกแก้จนกระทั่ง v3.1) หรือ pin `refs/tags/v3.0.0` ได้
- ไม่ freeze `formats-v3/` — geography มี 6 แถว การ freeze ทั้ง folder เพื่อ table เดียวซ้ำซ้อนกับข้อมูลอื่นที่ไม่เปลี่ยน; ถ้าต้องการ shape เก่าใช้ v2 snapshot พอ

---

## [3.0.0] - 2026-09-29

### Changed (⚠️ breaking)
- **Schema แยก `name` ออกจาก `prefix`** เป็น nested object — `{name: {th, en}, prefix: {th, en}}`
  - สมัยก่อน prefix บางแถว "ติดมาในชื่อ" (`name_th: "เขตพระนคร"`) บางแถวไม่มี (`name_th: "เมืองสมุทรปราการ"`) → ไม่สม่ำเสมอ
  - v3 ทุกแถวมี `prefix` ชัดเจน, `name` เป็น base name เท่านั้น
- **Province** ไม่มี prefix → `prefix: null` (คง key shape ให้สม่ำเสมอ)
- **Geography** ไม่เปลี่ยน (single `name` field, ไม่มี locale split)
- CSV/SQL/XLSX export **flatten** กลับเป็น 4 columns: `name_th`, `name_en`, `prefix_th`, `prefix_en` — SQL users ไม่ต้อง query JSON object
- JSON/XML/API export เก็บ nested ตาม source

### Added
- `scripts/migrate_v2_to_v3.py` — one-shot transform (idempotent guard)
- `api/v2/` — snapshot ของ v2 shape สำหรับ legacy consumers
- `formats-v2/` — snapshot ของ v2 formats (csv/json/sql/xlsx/xml)
- Validator (`0_validate_data.py`) รองรับ nested object schema โดย recurse เข้า `properties` ของ sub-object
- `1_export_file_format.py` เพิ่ม `flatten_row()` สำหรับ tabular exports; `dict_to_xml` recurse ได้แล้ว
- `prefix_th`/`prefix_en` VARCHAR(30) ใน SQL DDL (`districts`/`sub_districts` = NOT NULL, `provinces` = NULL allowed)

### Removed
- Dead code `load_spec_columns()` ใน `1_export_file_format.py` (return `[]` เสมอ, ไม่เคยถูกเรียก)
- Dead imports `sys`, `re`, `Optional`, `datetime` ใน `1_export_file_format.py`
- Dead `SPEC_FILES`/`SPEC_DIR` constants ใน `1_export_file_format.py` (ผู้ใช้เดียวคือ function ที่ลบ)
- Redundant `soft_name_trim_check` ใน `0_validate_data.py` — ซ้ำกับ trim check ใน `validate_against_schema` อยู่แล้ว

### Migration
- ถ้าใช้ `api/latest/` → data shape เปลี่ยนทันทีเมื่อ pull master
- ถ้าต้องการ v2 shape คงเดิม: switch URL ไป `api/v2/` (frozen)
- display helper:
  ```js
  const display = row.prefix ? `${row.prefix.th}${row.name.th}` : row.name.th;
  ```
  ```python
  display = f"{row['prefix']['th']}{row['name']['th']}" if row['prefix'] else row['name']['th']
  ```

---

## [2.0.0] - 2025-09-20

### Added
- อัปเดต **project structure** ใหม่เป็น version 2
- เพิ่ม `data/spec` สำหรับเก็บ JSON schema ของแต่ละ dataset (province, district, sub_district, geography)
- เพิ่ม `scripts/` สำหรับการทำงานอัตโนมัติ:
    - `0_validate_data.py` — ตรวจสอบความถูกต้องของข้อมูล
    - `1_export_file_format.py` — export data เป็นหลายรูปแบบ (CSV, JSON, SQL, XLSX, XML)
    - `2_export_api.py` — สร้าง API JSON สำหรับใช้งานโดยตรง
    - `make.sh` — run automation pipeline
- เพิ่ม **docs/schema.md** อธิบายโครงสร้างข้อมูลและความสัมพันธ์
- เพิ่ม **CONTRIBUTING.md** สำหรับแนวทางการมีส่วนร่วม

### Changed
- ปรับโครงสร้างโฟลเดอร์ใหม่ให้ชัดเจน:
    - `data/raw` → เก็บข้อมูลต้นทางจากหน่วยงาน
    - `data/spec` → เก็บ spec ของ dataset แต่ละประเภท
    - `formats/` → export หลายรูปแบบ (csv, json, sql, xlsx, xml)
    - `api/latest` → endpoint JSON ที่อัปเดตล่าสุด
    - `api/v1` → เก็บโครงสร้างเก่าเพื่อ backward compatibility
    - `docs/` → diagram, schema, readme
    - `scripts/` → pipeline automation
- ปรับชื่อ dataset:
    - **ลบ prefix `thai_`** จาก dataset ทั้งหมด
    - **rename:**
        - `amphure` → `district`
        - `tambon` → `sub_district`
        - `amphures` → `districts`
        - `tambons` → `sub_districts`
        - `tambons.amphure_id` → `sub_districts.district_id`
- ปรับ README.md ให้สอดคล้องกับโครงสร้างใหม่

### Removed
- Prefix `thai_` ในชื่อ dataset (เช่น `thai_provinces.csv` → `provinces.csv`)
- Legacy structure ที่ไม่สอดคล้องกับ v2 (ย้ายไป `api/v1/`)

---

## [1.0.0] - 2023-xx-xx

### Added
- Initial release
- ข้อมูลจังหวัด, อำเภอ (amphures), ตำบล (tambons) และโครงสร้างรวม
- Export หลายรูปแบบ (CSV, JSON, SQL, XLSX, XML)
- Diagram อธิบาย schema
- README.md และ LICENSE
