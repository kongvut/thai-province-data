# Contributing Guide

Thanks for your interest in **thai-province-data** — a dataset of Thailand's provinces, districts, and sub-districts.

[ไทย](CONTRIBUTING.md) | English

This is **open data** aggregated from official sources (Department of Provincial Administration, Thailand Post). Every PR needs a clear **reference** so the dataset stays trustworthy over time.

---

## Workflow

1. **Fork** the repo on GitHub.
2. **Branch from `master`**:
   ```bash
   git checkout -b fix-bueng-kan-zip
   ```
   Naming: `fix-<entity>-<short-issue>` or `add-<new-entity>` (e.g., `add-district-kanlapaphruek`, `update-sub-district-spelling`).
3. **Edit `data/raw/*.json` only** (also bump `updated_at` on touched rows). `formats/` and `api/latest/` are auto-regenerated artifacts.
4. **Validate + regenerate** (Docker — no local setup needed):
   ```bash
   docker compose build              # first time only (build image)
   docker compose run --rm make      # validate + export every time
   ```
   (No Docker? See [Pipeline (Python local)](#pipeline-python-local).)
5. **Commit** with short conventional prefixes:
   - `fix(data): correct zip code for sub_district 102601`
   - `add(data): new district กัลยาณิวัฒนา in Chiang Mai`
   - `docs: update API URL list in README`
6. **Open a PR** against `master` using the body template below.

---

## Data rules (v3 schema)

Source of truth: [`data/spec/*.json`](data/spec/). Schema changes are breaking — discuss in an issue first.

| Entity | field | Required? | Example |
|---|---|---|---|
| district | `name.th` / `name.en` | ✅ base name only | `"พระนคร"` / `"Phra Nakhon"` |
| district | `prefix.th` / `prefix.en` | ✅ **never null** | Bangkok → `"เขต"`/`"Khet"`, elsewhere → `"อำเภอ"`/`"Amphoe"` |
| sub_district | `prefix.th` / `prefix.en` | ✅ **never null** | Bangkok → `"แขวง"`/`"Khwaeng"`, elsewhere → `"ตำบล"`/`"Tambon"` |
| province | `prefix` | key must exist, value `null` | (provinces have no prefix convention) |
| all entities | `id` | primary key, no duplicates, never reassign an existing id | |

**Hard rules:**
- ❌ `name.th` must NOT include the prefix. `"เขตพระนคร"` is wrong → split to `name.th: "พระนคร"`, `prefix.th: "เขต"`.
- ❌ `name_th`/`name_en`/`prefix_th`/`prefix_en` (flat columns) are v2 schema. Don't reintroduce them.
- ❌ Renaming columns/keys in `data/spec/*.json` without an issue discussion is a breaking change.
- ❌ Never edit `api/v1/`, `api/v2/`, `formats-v2/` — they are frozen legacy snapshots.
- ❌ New `sub_district.district_id` must be a valid FK; the validator checks this.

**Edge case — "เมือง" capital districts:**
`name.th = "เมืองสมุทรปราการ"` (district id 1101) is the official full name of the capital district. "เมือง" is part of the **name**, not a prefix to strip. So: `prefix.th = "อำเภอ"`, `name.th = "เมืองสมุทรปราการ"` stays as-is.

---

## PR body template

```markdown
## Pull Request: <one-line summary>
Closes #<issue>

### Summary
<what changed and why>

### Changes
- `data/raw/districts.json` — add district กัลยาณิวัฒนา (id 5025)
- `data/raw/sub_districts.json` — move 3 sub_districts from Mae Chaem → Kanlapaphruek

### Reference
- <official URL — DOPA, Royal Gazette, or Thai Wikipedia with citation>

### Impact
- [ ] API endpoints (`api/latest/`) affected (regenerated via make.py)
- [ ] Format exports affected (regenerated)
- [ ] Breaking schema change (must be discussed in issue first)
```

**Real examples:** [PR #34](https://github.com/kongvut/thai-province-data/pull/34) — add new district · [PR #46](https://github.com/kongvut/thai-province-data/pull/46) — bulk restore from DOPA + Bueng Kan renumbering

---

## Review criteria

Maintainers check every PR against:

- ✅ **Validator passes**: `python3 scripts/0_validate_data.py --strict --fail-on-warn`
- ✅ **Regen matches commit**: `python3 scripts/make.py` → `formats/` + `api/latest/` must equal committed state
- ✅ **Reference provided**: every new or corrected row needs a source
- ✅ **Prefix correctness**: visually verify Bangkok vs non-Bangkok prefix mapping (most common bug)
- ✅ **CI workflow** (`validate-raw.yml`) green

Schema-changing PRs (add/rename field) must be discussed in an issue before opening a PR.

---

## Pipeline (Docker — recommended)

No Python/pandas/openpyxl install needed; environment matches CI.

```bash
docker compose build                    # first time only (image build)
docker compose run --rm validate        # validator only (strict + fail-on-warn)
docker compose run --rm make            # validate → export formats → export api
```

The repo is volume-mounted at `./:/app:rw` — edit `data/raw/*.json` on the host, the container sees it instantly, and regenerated outputs (`formats/`, `api/latest/`) write back into the same host directory.

**Fallback — Python local** (no Docker / working offline):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pandas openpyxl
```

Run the whole pipeline:

```bash
python3 scripts/make.py
```

Or step by step:

```bash
python3 scripts/0_validate_data.py --strict --fail-on-warn     # schema + FK + invariants
python3 scripts/1_export_file_format.py --overwrite            # CSV/SQL/XLSX/JSON/XML
python3 scripts/2_export_api.py --overwrite                    # api/latest/*.json
```

If validation fails, `make.py` exits 1 immediately (CI fails the same way).

## License

Every contribution merged into this repo is under the MIT License — see [LICENSE](LICENSE).
