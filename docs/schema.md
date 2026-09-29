# Schema (v3.1)

> Breaking change จาก v2: `name_th`/`name_en` (flat, มี prefix ในชื่อไม่สม่ำเสมอ) →
> `name: {th, en}` + `prefix: {th, en}` (nested, สม่ำเสมอ)
> Province ไม่มี prefix → `prefix: null` เพื่อคง key shape ให้ทุก entity
> v3.1: `geography.name` จาก string → nested `{th, en}` (geography ไม่มี prefix concept)

## Geography

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Geography",
  "type": "object",
  "properties": {
    "id": { "type": "integer", "description": "Primary key" },
    "name": {
      "type": "object",
      "properties": {
        "th": { "type": "string", "maxLength": 255 },
        "en": { "type": "string", "maxLength": 255 }
      },
      "required": ["th", "en"]
    }
  },
  "required": ["id", "name"]
}
```

(geography ไม่มี prefix → ไม่มีคีย์ `prefix`; ต่างจาก province ที่ `prefix: null`)

## Province

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Province",
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "name":   { "type": "object", "properties": { "th": {"type":"string","maxLength":150}, "en": {"type":"string","maxLength":150} }, "required": ["th","en"] },
    "prefix": { "type": ["object","null"], "properties": { "th": {"type":"string","maxLength":30}, "en": {"type":"string","maxLength":30} } },
    "geography_id": { "type": "integer" },
    "created_at": { "type": ["string","null"], "format": "date-time" },
    "updated_at": { "type": ["string","null"], "format": "date-time" },
    "deleted_at": { "type": ["string","null"], "format": "date-time" }
  },
  "required": ["id", "name", "prefix", "geography_id"]
}
```

## District

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "District",
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "name":   { "type": "object", "properties": { "th": {"type":"string","maxLength":150}, "en": {"type":"string","maxLength":150} }, "required": ["th","en"] },
    "prefix": { "type": "object", "properties": { "th": {"type":"string","maxLength":30}, "en": {"type":"string","maxLength":30} }, "required": ["th","en"] },
    "province_id": { "type": "integer" },
    "created_at": { "type": ["string","null"], "format": "date-time" },
    "updated_at": { "type": ["string","null"], "format": "date-time" },
    "deleted_at": { "type": ["string","null"], "format": "date-time" }
  },
  "required": ["id", "name", "prefix", "province_id"]
}
```

`prefix.th` = `"เขต"` สำหรับ กทม. districts, `"อำเภอ"` สำหรับต่างจังหวัด (รวม "เมืองX" capital districts)
`prefix.en` = `"Khet"` / `"Amphoe"`

## SubDistrict

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SubDistrict",
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "zip_code": { "type": "integer" },
    "name":   { "type": "object", "properties": { "th": {"type":"string","maxLength":150}, "en": {"type":"string","maxLength":150} }, "required": ["th","en"] },
    "prefix": { "type": "object", "properties": { "th": {"type":"string","maxLength":30}, "en": {"type":"string","maxLength":30} }, "required": ["th","en"] },
    "district_id": { "type": "integer" },
    "lat": { "type": ["number","null"] },
    "long": { "type": ["number","null"] },
    "created_at": { "type": ["string","null"], "format": "date-time" },
    "updated_at": { "type": ["string","null"], "format": "date-time" },
    "deleted_at": { "type": ["string","null"], "format": "date-time" }
  },
  "required": ["id", "zip_code", "name", "prefix", "district_id"]
}
```

`prefix.th` = `"แขวง"` สำหรับ sub_districts ใน กทม., `"ตำบล"` สำหรับต่างจังหวัด
`prefix.en` = `"Khwaeng"` / `"Tambon"`

## การ render สำหรับ display

```python
# Python
display_name = f"{row['prefix']['th']}{row['name']['th']}" if row['prefix'] else row['name']['th']
# → "เขตพระนคร", "อำเภอเมืองสมุทรปราการ", "กรุงเทพมหานคร"
```

```js
// JS
const display = row.prefix ? `${row.prefix.th}${row.name.th}` : row.name.th;
```

## Export formats: nested → flattened columns

JSON / XML / API: เก็บ nested ตาม source
CSV / SQL / XLSX: flatten `name` → `name_th`, `name_en`; `prefix` → `prefix_th`, `prefix_en` (null สำหรับ province)

## Province With District And SubDistrict

```json
{
  "type": "object",
  "allOf": [
    { "$ref": "#/definitions/province" },
    {
      "properties": {
        "districts": {
          "type": "array",
          "items": {
            "allOf": [
              { "$ref": "#/definitions/district" },
              {
                "properties": {
                  "sub_districts": {
                    "type": "array",
                    "items": { "$ref": "#/definitions/sub_district" }
                  }
                }
              }
            ]
          }
        }
      }
    }
  ]
}
```

## SubDistrict With District And Province

```json
{
  "type": "object",
  "allOf": [
    { "$ref": "#/definitions/sub_district" },
    {
      "properties": {
        "district": {
          "allOf": [
            { "$ref": "#/definitions/district" },
            {
              "properties": {
                "province": { "$ref": "#/definitions/province" }
              }
            }
          ]
        }
      }
    }
  ]
}
```
