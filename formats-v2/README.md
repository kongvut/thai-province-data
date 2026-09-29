# `formats-v2/` — frozen legacy snapshot

เก็บ export files ของ **v2** (CSV/SQL/XLSX flatten ไม่มี `prefix_th`/`prefix_en` columns, JSON `name_th` มี prefix ติดมาใน string)
เพื่อ backward compatibility — consumer ที่ download `formats-v2/csv/districts.csv` จะได้ shape เดิมตลอด

**ห้ามแก้ไข**: ไฟล์ในนี้เป็น snapshot copy ของ `formats/` ณ version ก่อน v3.0.0

- v3 schema → `data/spec/*.json`, `docs/schema.md`
- Migration notes → [`CHANGELOG.md`](../CHANGELOG.md) (`[3.0.0]` section)
- v3 output → `formats/`
