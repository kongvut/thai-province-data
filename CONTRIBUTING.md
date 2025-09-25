# Contributing Guide

ขอบคุณที่สนใจร่วมพัฒนา **thai-province-data** 🎉  
โปรเจกต์นี้เป็นฐานข้อมูล **จังหวัด, อำเภอ (district), ตำบล (sub_district)** ของประเทศไทย  
สามารถใช้งานได้หลายรูปแบบ (CSV, JSON, SQL, XLSX, XML, API) และเปิดกว้างสำหรับการร่วมพัฒนา

---

## 🛠️ ขั้นตอนการมีส่วนร่วม

1. **Fork repository** ไปยัง GitHub ของคุณ
2. **สร้าง branch ใหม่** สำหรับการแก้ไข/เพิ่มข้อมูล
   ```bash
   git checkout -b fix-district-name
   ```
   ตัวอย่างชื่อ branch ที่แนะนำ:
    - `fix-district-name`
    - `update-postal-code`
    - `add-new-district-data`
3. ทำการแก้ไขหรือเพิ่มข้อมูลที่ไฟล์ (และอัปเดทเวลาเมื่อแก้ไขข้อมูล `updated_at`) `data/raw/*.json`

   > note: รบกวนแก้ไขไฟล์ที่ `data/raw/*.json` เท่านั้น เพราะ API และ File format ต่าง ๆ จะถูก Generate อัตโนมัติในขั้นตอนที่ 4
4. **ตรวจสอบข้อมูลก่อนส่ง PR**
   ```bash
   python3 scripts/0_validate_data.py --strict --fail-on-warn
   python3 scripts/make.py
   ```
   > สำหรับผู้ที่ไม่ต้องการติดตั้ง Python และ dependency เอง สามารถใช้ Docker ได้ทันทีที่นี่ "[การใช้งานด้วย Docker](#1-build-image)"
5. Commit การเปลี่ยนแปลงด้วยข้อความสั้น กระชับ:
   ```bash
   fix: correct zip code in sub_districts
   add: new district in Chiang Mai
   docs: update README for API usage
   ```
6. เปิด **Pull Request (PR)** มายัง branch `main` พร้อมคำอธิบายที่ชัดเจน

---

## 📂 โครงสร้างข้อมูล

- `data/raw/` → ไฟล์ต้นทาง (JSON array)
- `data/spec/` → JSON Schema ของแต่ละตาราง
- `formats/` → ไฟล์ export หลายรูปแบบ (csv/json/sql/xlsx/xml)
- `api/latest/` → API JSON ที่ build แล้วจาก raw data

---

## ✅ สิ่งที่ทำได้

- แก้ไขข้อมูลสะกดผิด (`name_th`, `name_en`)
- ปรับปรุง **รหัสไปรษณีย์ / lat / long**
- เพิ่มข้อมูลใหม่จาก **หน่วยงานรัฐ/แหล่งทางการ**
- ปรับปรุง **เอกสาร** (README, Docs, Schema)
- เพิ่มรูปแบบ export ใหม่ (เช่น **Parquet, GeoJSON**)
- ปรับปรุงสคริปต์ใน `scripts/` ให้ใช้งานง่ายขึ้น

---

## 🔒 สิ่งที่ควรระวัง

- ต้องคง **schema** ตามที่กำหนดใน `data/spec/`
- ห้ามเปลี่ยนชื่อคอลัมน์/keys โดยพลการ
- ข้อมูลใหม่ควรมี **reference ที่ชัดเจน**
- หลีกเลี่ยงการ commit ไฟล์ที่ไม่เกี่ยวข้อง (`.DS_Store`, `*.log`, `node_modules/`)

---

## 📄 ตัวอย่าง Pull Request

เวลาเปิด PR กรุณาระบุรายละเอียด เช่น:

```markdown
### Summary
แก้ไขชื่ออำเภอ "เมืองขอนแก่น" ในไฟล์ districts.json และ districts.csv

### Changes
- data/raw/districts.json
- formats/csv/districts.csv

### Reference
ข้อมูลจากกรมการปกครอง: https://www.dopa.go.th/

### Impact
ไม่มีผลกระทบต่อ schema หรือ API JSON
```

---

## 🧑‍💻 สำหรับนักพัฒนา

### ติดตั้ง environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pandas openpyxl
```

### รันสคริปต์แยก
- ตรวจสอบข้อมูล: `python3 scripts/0_validate_data.py --strict --fail-on-warn`
- export formats: `python3 scripts/1_export_file_format.py --overwrite`
- export api: `python3 scripts/2_export_api.py --overwrite`

---

## 🧰 Automation Pipeline

สามารถรัน pipeline ได้ด้วยคำสั่งเดียว:

```bash
python3 scripts/make.py
```

Pipeline จะทำงานดังนี้:
1. รัน `0_validate_data.py` ตรวจสอบข้อมูล
2. รัน `1_export_file_format.py --overwrite` สร้าง formats
3. รัน `2_export_api.py --overwrite` อัปเดต API JSON

---

## 🐳 การใช้งานด้วย Docker

สำหรับผู้ที่ไม่ต้องการติดตั้ง Python และ dependency เอง สามารถใช้ Docker ได้ทันที

### 1) Build image
```bash
docker compose build
```

### 2) รัน validator
```bash
docker compose run --rm validate
```

### 3) รัน pipeline เต็ม (validate → export formats → export api)
```bash
docker compose run --rm make
```

### 4) อธิบายโครงสร้างไฟล์ที่ใช้ร่วมกับ Docker
- [Dockerfile](/Dockerfile) — กำหนด environment และ dependency
- [docker-compose.yml](/docker-compose.yml) — service สำหรับ `validate` และ `make`
- mount โฟลเดอร์ปัจจุบัน (`./`) ไปยัง `/app` ใน container เพื่อให้แก้ไขข้อมูลใน repo แล้วสามารถรันได้ทันที

> เหมาะสำหรับผู้ใช้ที่ต้องการความสะดวก ไม่ต้องติดตั้ง Python, pandas, openpyxl ในเครื่อง

## 🤝 การ Review & Merge

- Maintainer จะตรวจสอบ PR ทุกครั้ง
- ถ้าข้อมูลถูกต้องและมี reference → PR จะถูก merge
- ถ้ามีปัญหา จะมีการ comment ให้แก้ไขก่อน

---

🙏 ขอบคุณสำหรับการมีส่วนร่วม  
สิ่งที่คุณช่วยปรับปรุง จะช่วยให้ dataset นี้ **แม่นยำ ครอบคลุม และมีประโยชน์ต่อผู้ใช้งานทุกคน**
