# Data Model Diagram

แผนภาพความสัมพันธ์ข้อมูล (Entity–Relationship Diagram, ERD)  
ครอบคลุมโครงสร้าง: **Geographies → Provinces → Districts → Sub-districts**

---

## 📊 ERD (Entity–Relationship Diagram)

```mermaid
erDiagram
    GEOGRAPHIES {
        int id PK
        string name
    }

    PROVINCES {
        int id PK
        string name_th
        string name_en
        int geography_id FK
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }

    DISTRICTS {
        int id PK
        string name_th
        string name_en
        int province_id FK
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }

    SUB_DISTRICTS {
        int id PK
        int zip_code
        string name_th
        string name_en
        int district_id FK
        double lat
        double long
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }

    GEOGRAPHIES ||--o{ PROVINCES : "1..*"
    PROVINCES   ||--o{ DISTRICTS : "1..*"
    DISTRICTS   ||--o{ SUB_DISTRICTS : "1..*"
```

---

## 🌳 Hierarchy View

โครงสร้างแบบลำดับชั้น (Hierarchy) ช่วยให้เห็นความเชื่อมโยงของข้อมูลจากบนลงล่าง

```mermaid
flowchart TD
    G[Geographies] --> P[Provinces]
    P[Provinces] --> D[Districts]
    D[Districts] --> S[Sub-districts]

    G --- Gf["id, name"]
    P --- Pf["id, name_th, name_en, geography_id, created_at, updated_at, deleted_at"]
    D --- Df["id, name_th, name_en, province_id, created_at, updated_at, deleted_at"]
    S --- Sf["id, zip_code, name_th, name_en, district_id, lat, long, created_at, updated_at, deleted_at"]
```

---

## 📖 Legend

- **PK** → Primary Key
- **FK** → Foreign Key
- เส้น `||--o{` = ความสัมพันธ์แบบ **One-to-Many (1..*)**

---

## 📝 หมายเหตุ

- ตาราง **geographies** เป็น root → provinces
- ตาราง **provinces** เชื่อมโยงกับ geographies ผ่าน `geography_id`
- ตาราง **districts** เชื่อมโยงกับ provinces ผ่าน `province_id`
- ตาราง **sub_districts** เชื่อมโยงกับ districts ผ่าน `district_id`
- ทุกตารางมี **timestamps** (`created_at`, `updated_at`, `deleted_at`) เพื่อรองรับการ track การเปลี่ยนแปลงข้อมูล

