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
3. ทำการแก้ไขหรือเพิ่มข้อมูล
4. **ตรวจสอบข้อมูลก่อนส่ง PR**
   ```bash
   python3 scripts/0_validate_data.py --strict --fail-on-warn
   python3 scripts/make.py
   ```
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

> รายละเอียดเพิ่มเติมสำหรับนักพัฒนา "[การติดตั้ง environment สำหรับรัน scripts](./docs/readme.md)"

## 🤝 การ Review & Merge

- Maintainer จะตรวจสอบ PR ทุกครั้ง
- ถ้าข้อมูลถูกต้องและมี reference → PR จะถูก merge
- ถ้ามีปัญหา จะมีการ comment ให้แก้ไขก่อน

---

🙏 ขอบคุณสำหรับการมีส่วนร่วม  
สิ่งที่คุณช่วยปรับปรุง จะช่วยให้ dataset นี้ **แม่นยำ ครอบคลุม และมีประโยชน์ต่อผู้ใช้งานทุกคน**  
