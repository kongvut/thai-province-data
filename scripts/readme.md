# 🧪 สคริปต์ & Automation

## ติดตั้ง environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pandas openpyxl
```

## 🧪 0_validate_data.py

[0_validate_data.py](0_validate_data.py) สคริปต์นี้ใช้เพื่อ validate ข้อมูลต้นฉบับก่อนส่ง PR

- โหลด spec จาก data/spec/*.json (singular: geography.json, province.json, district.json, sub_district.json)
- โหลด raw data จาก data/raw/*.json (plural: geographies.json, provinces.json, districts.json, sub_districts.json)
- ตรวจตามสเปค (required, type, maxLength, format: date-time แบบ ISO8601)
- ตรวจความซ้ำของ id 
- ตรวจ FK: provinces.geography_id → geographies.id, districts.province_id → provinces.id, sub_districts.district_id → districts.id 
- ตรวจ zip_code เป็นตัวเลข 5 หลัก, lat/long อยู่ในช่วงที่ถูกต้อง 
- รายงาน Errors/Warnings และคืนค่า exit code 1 เมื่อมี error (หรือ warning หากเลือก --fail-on-warn)

> ใช้ มาตรฐาน JSON Schema แบบย่อ (ไม่พึ่งไลบรารีภายนอก) เพื่อความสะดวกในการรันบนเครื่อง/CI ที่ไม่มีการติดตั้งเพิ่ม

### วิธีใช้งาน

```bash
# จาก root ของ repo
python3 scripts/0_validate_data.py --strict --fail-on-warn
```

## 🧪 1_export_file_format.py

[1_export_file_format.py](1_export_file_format.py) สคริปต์นี้ใช้เพื่อสำหรับ export จาก data/raw/*.json ไปเป็นข้อมูลเป็นไฟล์ต่าง ๆ ตาม format ที่ต้องการ (CSV, JSON, SQL, XLSX, XML)

- อ่าน input:

    `data/raw/geographies.json`, `provinces.json`, `districts.json`, `sub_districts.json` 
- เขียน output:

  `formats/{csv,json,sql,xlsx,xml}/<table>.(ext)`
- ใช้ spec เพื่อจัดลำดับคอลัมน์ให้คงที่ 
- SQL จะมีทั้ง CREATE TABLE (ตาม DDL ที่ให้มา) + INSERT ครบทุกรายการ 
- รองรับ flag:
  - --root ระบุ repo root (ดีฟอลต์: โฟลเดอร์บน)
  - --indent 2 กำหนด JSON indent 
  - --overwrite ทับไฟล์เดิมได้ 
  - --no-create ให้ข้ามการเขียน SQL CREATE TABLE (เหลือเฉพาะ INSERT)

> Dependencies สำหรับ XLSX: pandas, openpyxl (ถ้าไม่มี สคริปต์จะยัง export format อื่น ๆ ได้ และจะเตือนเฉย ๆ)

### วิธีใช้งาน

```bash
# จาก root ของ repo
python3 scripts/0_validate_data.py --strict --fail-on-warn
python3 scripts/1_export_file_format.py --indent 2 --overwrite
```

## 🧪 2_export_api.py

[2_export_api.py](2_export_api.py) สคริปต์นี้ใช้ข้อมูลจาก `data/raw/*.json` แล้วส่งออกไฟล์ API ไปยัง `api/latest/`:

- api/latest/province.json 
- api/latest/district.json 
- api/latest/sub_district.json 
- api/latest/province_with_district_and_sub_district.json 
- api/latest/sub_district_with_district_and_province.json

สคริปต์นี้:

- รองรับ --root (กำหนด repo root), --indent (ระดับย่อหน้า JSON), --overwrite (ยอมให้ทับไฟล์)
- เรียงลำดับคีย์ให้อ่านง่ายตามสคีมา (เช่น id, name_th, name_en, ...)
- ทำ deep copy ของข้อมูลเมื่อนำไป nest เพื่อไม่แก้ไขต้นฉบับ 
- ข้ามการฝัง (nest) หาก FK ไม่พบ (พร้อมพิมพ์คำเตือน)

### การใช้งาน

```bash
# จาก root ของ repo
python3 scripts/2_export_api.py --indent 2 --overwrite
```

## 🧪 make.py

make.py เป็นตัว orchestrator ของ pipeline ซึ่งจะ:

- รัน 0_validate_data.py (ตรวจสอบข้อมูล)
- รัน 1_export_file_format.py --overwrite (แปลงเป็น CSV/JSON/SQL/XLSX/XML)
- รัน 2_export_api.py --overwrite (สร้างไฟล์ API JSON)

> ถ้าสเต็ปไหน error → หยุดทันที และคืนค่า exit code ไม่ให้ไปต่อ

### การใช้งาน

```bash
python3 scripts/make.py
```


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

### 4) โครงสร้างไฟล์ที่ใช้ร่วมกับ Docker
- `Dockerfile` — กำหนด environment และ dependency
- `docker-compose.yml` — service สำหรับ `validate` และ `make`
- mount โฟลเดอร์ปัจจุบัน (`./`) ไปยัง `/app` ใน container เพื่อให้แก้ไขข้อมูลใน repo แล้วสามารถรันได้ทันที

> เหมาะสำหรับผู้ใช้ที่ต้องการความสะดวก ไม่ต้องติดตั้ง Python, pandas, openpyxl ในเครื่อง

## 🤝 Contributing
- โปรดอ่าน [CONTRIBUTING.md](../CONTRIBUTING.md) ก่อนส่ง PR
