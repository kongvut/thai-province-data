# AGENTS.md — thai-province-data

Project context for AI coding agents (Qwen Code, Codex, Cursor, Zed, etc.).
Human-facing docs: [README.md](README.md) · [CONTRIBUTING.md](CONTRIBUTING.md) · [CHANGELOG.md](CHANGELOG.md).

## What this is

Thailand **province / district / sub-district** dataset, published as:
- `data/raw/*.json` — **source of truth** (hand-edited here)
- `data/spec/*.json` — JSON Schema per entity (validator + pipeline read these directly)
- Generated outputs: `formats/{csv,json,sql,xlsx,xml}/` and `api/latest/` (never hand-edit — regenerate)

Served publicly over GitHub raw from `master`.

## Repository layout

```
api/latest/    → v3 nested JSON (primary API)
api/v2/ api/v1 → FROZEN legacy snapshots (do not edit)
data/raw/      → JSON source of truth  ← edit here
data/spec/     → JSON Schema (province/district/sub_district/geography)
formats/       → v3 export: csv/json/sql/xlsx/xml  (generated)
formats-v2/    → FROZEN legacy formats (do not edit)
docs/          → schema.md, diagram.md
scripts/       → pipeline (validate, export, make, migrate)
.github/workflows/validate-raw.yml → CI
```

## Schema (v3.1) — the core invariant

Every entity uses **nested language objects**. `name` is the base name WITHOUT its prefix; `prefix` is separate.

| entity | fields | notes |
|---|---|---|
| `geography` | `id`, `name{th,en}` | **no `prefix` field** (regions have no prefix concept) |
| `province` | `id`, `name{th,en}`, `prefix`, `geography_id`, timestamps | `prefix: null` (kept for key-shape uniformity) |
| `district` | `id`, `name{th,en}`, `prefix{th,en}`, `province_id`, timestamps | prefix never null |
| `sub_district` | `id`, `zip_code`, `name{th,en}`, `prefix{th,en}`, `district_id`, `lat`, `long`, timestamps | prefix never null |

Example district:
```json
{ "id": 1001, "name": { "th": "พระนคร", "en": "Phra Nakhon" },
  "prefix": { "th": "เขต", "en": "Khet" }, "province_id": 1 }
```

**Display rule:** `prefix.th + name.th` (Thai attaches directly, e.g. `เขตพระนคร`); for provinces (`prefix` null) use `name.th` alone. English: `prefix.en + " " + name.en` (space).

**Prefix conventions (never mix up):**
- Bangkok (`province_id == 1`): district `เขต`/`Khet`, sub-district `แขวง`/`Khwaeng`
- Everywhere else: district `อำเภอ`/`Amphoe`, sub-district `ตำบล`/`Tambon`
- `เมือง`-prefixed capital districts (e.g. `เมืองสมุทรปราการ`) keep `เมือง…` **inside `name.th`**; `prefix` stays `อำเภอ`. Do not strip.

**Tabular exports flatten, structured exports keep nested:**
- CSV / SQL / XLSX → `name_th`, `name_en`, `prefix_th`, `prefix_en` (via `flatten_row()` in `1_export`)
- JSON / XML / api → nested `{th, en}` as in source
- SQL DDL: `prefix_*` VARCHAR(30), NOT NULL for district/sub_district, nullable for province; geography `name_*` VARCHAR(255)

## Running the pipeline

**Preferred — Docker** (matches CI Python 3.11, no local setup):
```bash
docker compose build                 # first time
docker compose run --rm validate     # validator only: 0_validate_data.py --strict --fail-on-warn
docker compose run --rm make         # full: validate → export formats → export api
```
Repo is volume-mounted at `/app:rw`; outputs write straight back to the host tree.

**Fallback — local Python** (needs `pandas` + `openpyxl`):
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -U pandas openpyxl
python3 scripts/make.py
```

Scripts (each supports `--help`, `--root <dir>`):
- `0_validate_data.py` — schema (recursive nested-object support), FK, unique id, zip/lat/long checks
- `1_export_file_format.py` — `formats/{csv,json,sql,xlsx,xml}/<table>` · `--overwrite`, `--no-create` (skip SQL DDL)
- `2_export_api.py` — 5 API files in `api/latest/` · `--overwrite` (does **not** read geographies)
- `make.py` — orchestrates 0 → 1 → 2. **Note:** make.py runs the validator *without* `--strict/--fail-on-warn`; CI runs it *with* them.
- `migrate_v2_to_v3.py` — one-shot v2 flat → v3 nested transform, idempotent guard, `--dry-run`

## Golden rules for changes

1. **Edit only `data/raw/*.json`** (and `data/spec/*.json` for schema changes). Bump `updated_at` on rows you touch.
2. **Never hand-edit `formats/` or `api/latest/`** — run `docker compose run --rm make` and commit the regenerated files.
3. **Never edit `api/v1/`, `api/v2/`, `formats-v2/`** — frozen backward-compat snapshots.
4. Schema changes (add/rename field, change type) are **breaking** → must be discussed in an issue first, get a `CHANGELOG.md` entry, and consider a legacy snapshot fallback.
5. Every new/changed data row needs a citation (DOPA / Royal Gazette / Thai Wikipedia) in the PR.

## CI (`.github/workflows/validate-raw.yml`)

Triggers on PRs + pushes touching `data/raw/**`, `data/spec/**`, `scripts/*`, workflow itself. Steps:
1. `python3 scripts/0_validate_data.py --strict --fail-on-warn` (must exit 0)
2. **Regen-drift check** — re-run `1_export` + `2_export`, then `git diff --quiet formats/{csv,json,sql,xml} api/latest/`. If your committed outputs don't match a fresh regen, CI fails.
3. **`formats/xlsx/` is excluded** from drift: openpyxl embeds a creation timestamp so xlsx bytes differ every run even when content is identical. → After regen, the unrelated xlsx files may show timestamp-only diffs; restore them (`git restore --source=HEAD formats/xlsx/...`) to keep the diff focused; only commit xlsx whose actual data changed.

**Before opening a PR, verify:** `docker compose run --rm validate` passes AND regen is idempotent (re-run `make`, `sha256sum` of `formats/{csv,json,sql,xml}` + `api/latest` unchanged).

## Conventions

- **Version:** current line is **3.x.x**. v4.0.0 is reserved for a large, coordinated change (e.g. geography rework, coordinates completeness, per-row provenance). Small breaking schema tweaks ride a minor bump (v3.0.0 → v3.1.0 = geography nested) with `CHANGELOG` + fallback notes.
- **Commits:** Conventional Commits (`feat`/`fix`/`docs`/`chore`/`refactor`); commit messages are self-contained PR descriptions (what + why).
- **PR template** lives in [CONTRIBUTING.md](CONTRIBUTING.md); branch naming `fix-<entity>-<issue>` / `add-<entity>`.
- **Docs come in TH/EN pairs** — if you edit `README.md`, mirror to `README.en.md`; same for `CONTRIBUTING.md` / `CONTRIBUTING.en.md`.

## Gotchas

- `api/latest/` has 5 files, not 4 — geography is NOT an API entity; it appears only in `formats/`. Province links to region via `geography_id` (int).
- Migration of geography to nested (`data/raw/geographies.json`) was done directly (6 rows), not via a migrate script.
- The public URL uses `refs/heads/master/...`; for immutable pinning use `refs/tags/v3.0.0/...` (and future tags).
