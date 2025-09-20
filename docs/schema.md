# Schema

## Geography

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Geography",
  "type": "object",
  "properties": {
    "id": { "type": "integer", "description": "Primary key" },
    "name": { "type": "string", "maxLength": 255 }
  },
  "required": ["id", "name"]
}
```

## Province

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Province",
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "name_th": { "type": "string", "maxLength": 150 },
    "name_en": { "type": "string", "maxLength": 150 },
    "geography_id": { "type": "integer" },
    "created_at": { "type": ["string","null"], "format": "date-time" },
    "updated_at": { "type": ["string","null"], "format": "date-time" },
    "deleted_at": { "type": ["string","null"], "format": "date-time" }
  },
  "required": ["id", "name_th", "name_en", "geography_id"]
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
    "name_th": { "type": "string", "maxLength": 150 },
    "name_en": { "type": "string", "maxLength": 150 },
    "province_id": { "type": "integer" },
    "created_at": { "type": ["string","null"], "format": "date-time" },
    "updated_at": { "type": ["string","null"], "format": "date-time" },
    "deleted_at": { "type": ["string","null"], "format": "date-time" }
  },
  "required": ["id", "name_th", "name_en", "province_id"]
}
```

## SubDistrict

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SubDistrict",
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "zip_code": { "type": "integer" },
    "name_th": { "type": "string", "maxLength": 150 },
    "name_en": { "type": "string", "maxLength": 150 },
    "district_id": { "type": "integer" },
    "lat": { "type": ["number","null"] },
    "long": { "type": ["number","null"] },
    "created_at": { "type": ["string","null"], "format": "date-time" },
    "updated_at": { "type": ["string","null"], "format": "date-time" },
    "deleted_at": { "type": ["string","null"], "format": "date-time" }
  },
  "required": ["id", "zip_code", "name_th", "name_en", "district_id"]
}
```

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
