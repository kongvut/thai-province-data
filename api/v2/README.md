# `api/v2/` — frozen legacy snapshot

เก็บ data shape ของ **v2** (flat `name_th`/`name_en`, prefix `เขต`/`Khet` ติดมาใน string)
เพื่อ backward compatibility — ผู้ใช้เดิมที่ consume raw URL `api/v2/district.json` จะได้ shape เดิมตลอด

**ห้ามแก้ไข**: ไฟล์ในนี้เป็น snapshot copy ของ `api/latest/` ณ version ก่อน v3.0.0

- v3 schema → `../data/spec/*.json`, `../docs/schema.md`
- Migration notes → [`../CHANGELOG.md`](../CHANGELOG.md) (`[3.0.0]` section)
- v3 output → `../api/latest/`
