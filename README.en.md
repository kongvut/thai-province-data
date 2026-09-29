# Thai Province Data

[![GitHub stars](https://img.shields.io/github/stars/kongvut/thai-province-data.svg)](https://github.com/kongvut/thai-province-data/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kongvut/thai-province-data.svg)](https://github.com/kongvut/thai-province-data/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A dataset of **provinces / districts / sub-districts** of Thailand, distributed in CSV, JSON, SQL, XLSX, XML, plus JSON API files served straight from GitHub raw URLs.

[ไทย](README.md) | English

> **v3** — schema separates `name` from `prefix` as nested objects (breaking change).
> Migration notes in [CHANGELOG.md](CHANGELOG.md) · v2 shape preserved at [api/v2/](api/v2/) and [formats-v2/](formats-v2/)

---

## Layout

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

Source of truth = `data/spec/*.json` (validator and pipeline read these directly).

| entity | fields |
|---|---|
| `geography` | `id`, `name` |
| `province` | `id`, `name{th,en}`, `prefix` (null), `geography_id`, timestamps |
| `district` | `id`, `name{th,en}`, `prefix{th,en}`, `province_id`, timestamps |
| `sub_district` | `id`, `zip_code`, `name{th,en}`, `prefix{th,en}`, `district_id`, `lat`, `long`, timestamps |

Example district:

```json
{
  "id": 1001,
  "name":   { "th": "พระนคร", "en": "Phra Nakhon" },
  "prefix": { "th": "เขต",    "en": "Khet" },
  "province_id": 1
}
```

**Display**: `prefix.th + name.th` → `"เขตพระนคร"`. For provinces, `prefix === null` so use `name.th` alone.

**Tabular exports** (CSV/SQL/XLSX) flatten to `<field>_th` / `<field>_en` columns; JSON/XML keep nested.

Full schema + ERD: [docs/schema.md](docs/schema.md), [docs/diagram.md](docs/diagram.md)

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

React dropdown demo (cascading district/sub-district): <https://codesandbox.io/p/sandbox/thailand-province-demo-api-k3st7>

---

## Use in code

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

**Recommended: Docker** (no Python/dependency setup; matches CI):

```bash
docker compose build
docker compose run --rm make
```

**Local Python** (if Docker is inconvenient — requires `pandas` + `openpyxl`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U pandas openpyxl
python3 scripts/make.py
```

Per-script details → [scripts/readme.md](scripts/readme.md)

---

## Contributing

- Read [CONTRIBUTING.en.md](CONTRIBUTING.en.md) before opening a PR
- **Do not modify** files under `api/v1/`, `api/v2/`, `formats-v2/` — they are frozen legacy snapshots
- New district / sub_district rows must set `prefix` correctly: Bangkok → `เขต`/`แขวง` (`Khet`/`Khwaeng`); other provinces → `อำเภอ`/`ตำบล` (`Amphoe`/`Tambon`). See the rules table in CONTRIBUTING.en.md

## History

Breaking changes and migration notes → [CHANGELOG.md](CHANGELOG.md)

## License

MIT © 2025 Kongvut Sangkla → [LICENSE](LICENSE)
