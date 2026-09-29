# Thai Province Data

[![GitHub stars](https://img.shields.io/github/stars/kongvut/thai-province-data.svg)](https://github.com/kongvut/thai-province-data/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kongvut/thai-province-data.svg)](https://github.com/kongvut/thai-province-data/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ชุดข้อมูล **จังหวัด / อำเภอ / ตำบล** ของประเทศไทย พร้อมใช้หลายรูปแบบ (CSV, JSON, SQL, XLSX, XML) และ API JSON ผ่าน GitHub raw URL

ไทย | [English](README.en.md)

> **v3** — schema แยก `name` ออกจาก `prefix` เป็น nested object (breaking change)
> รายละเอียด + migration ที่ [CHANGELOG.md](CHANGELOG.md) · shape เก่าคงอยู่ที่ [api/v2/](api/v2/) และ [formats-v2/](formats-v2/)

---

## โครงสร้าง

```
api/latest/                → v3 nested JSON (primary)
api/v2/                    → frozen v2 snapshot (legacy)
api/v1/                    → frozen v1 (amphure/tambon naming)
data/raw/                  → JSON source of truth
data/spec/                 → JSON Schema (validator + pipeline input)
formats/                   → v3 export: csv/json/sql/xlsx/xml
formats-v2/                → frozen v2 formats (legacy)
docs/                      → schema.md, diagram.md
scripts/                   → pipeline (validate, export, make)
```

## Schema

Source-of-truth = `data/spec/*.json` (validator และ pipeline อ่านจากไฟล์นี้ตรง ๆ)

| entity | fields |
|---|---|
| `geography` | `id`, `name` |
| `province` | `id`, `name{th,en}`, `prefix` (null), `geography_id`, timestamps |
| `district` | `id`, `name{th,en}`, `prefix{th,en}`, `province_id`, timestamps |
| `sub_district` | `id`, `zip_code`, `name{th,en}`, `prefix{th,en}`, `district_id`, `lat`, `long`, timestamps |

ตัวอย่าง district:

```json
{
  "id": 1001,
  "name":   { "th": "พระนคร", "en": "Phra Nakhon" },
  "prefix": { "th": "เขต",    "en": "Khet" },
  "province_id": 1
}
```

**Display**: `prefix.th + name.th` → `"เขตพระนคร"` (province → `prefix === null` → ใช้ `name.th` เฉย)

**Tabular exports** (CSV/SQL/XLSX) flatten เป็น `<field>_th` / `<field>_en` columns; JSON/XML เก็บ nested

รายละเอียด + ERD → [docs/schema.md](docs/schema.md), [docs/diagram.md](docs/diagram.md)

---

## API URLs (GitHub raw)

| endpoint | URL |
|---|---|
| province | `https://raw.githubusercontent.com/kongvut/thai-province-data/refs/heads/master/api/latest/province.json` |
| district | `…/api/latest/district.json` |
| sub_district | `…/api/latest/sub_district.json` |
| province → districts → sub_districts | `…/api/latest/province_with_district_and_sub_district.json` |
| sub_district → district → province | `…/api/latest/sub_district_with_district_and_province.json` |

```bash
curl -s https://raw.githubusercontent.com/kongvut/thai-province-data/refs/heads/master/api/latest/province.json | jq '.[0:3]'
```

React dropdown demo (cascade อำเภอ/ตำบล): <https://codesandbox.io/p/sandbox/thailand-province-demo-api-k3st7>

---

## ใช้งานด้วยโค้ด

**Python**
```python
import requests

url = "https://raw.githubusercontent.com/kongvut/thai-province-data/refs/heads/master/api/latest/district.json"
districts = requests.get(url).json()

d = districts[0]
display_th = f"{d['prefix']['th']}{d['name']['th']}"   # "เขตพระนคร"
```

**Node.js**
```js
const url = "https://raw.githubusercontent.com/kongvut/thai-province-data/refs/heads/master/api/latest/district.json";
const districts = await (await fetch(url)).json();

const d = districts[0];
const displayTh = `${d.prefix.th}${d.name.th}`;   // "เขตพระนคร"
```

---

## Pipeline

**แนะนำ: Docker** (ไม่ต้อง setup Python/dependencies เอง; ตรงกับ CI):

```bash
docker compose build
docker compose run --rm make
```

**Local Python** (ถ้าไม่สะดวกใช้ Docker — ต้องมี `pandas` + `openpyxl`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U pandas openpyxl
python3 scripts/make.py
```

รายละเอียด script ทีละ step → [scripts/readme.md](scripts/readme.md)

---

## พัฒนาต่อ

- อ่าน [CONTRIBUTING.md](CONTRIBUTING.md) ก่อนเปิด PR
- **ห้ามแก้** ไฟล์ใน `api/v1/`, `api/v2/`, `formats-v2/` (frozen legacy snapshots)
- district/sub_district row ใหม่ต้องใส่ `prefix` ให้ถูกประเภท (เขต/แขวง สำหรับ กทม.; อำเภอ/ตำบล สำหรับต่างจังหวัด) — ดู rule ใน CONTRIBUTING.md

## History

Breaking changes + migration notes → [CHANGELOG.md](CHANGELOG.md)

## License

MIT © 2025 Kongvut Sangkla → [LICENSE](LICENSE)
