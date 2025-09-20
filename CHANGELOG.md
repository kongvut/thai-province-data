# Changelog

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
