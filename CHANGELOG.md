# Changelog

## Unreleased

- A file under `operations/` that cannot be read (permission denied, locked by a sync client, or a
  folder named like `*.yaml`) is now reported as a `Y001` finding instead of crashing with a traceback.

## 1.0.0 (2026-11-26)

First release.

- YAML inventory: `organization.yaml` plus one file per processing operation.
- JSON Schema with the codes of LGPD arts. 5, II, 7, 11 and 33.
- `ropa-kit init`, `validate` (text or JSON, `--strict`), `report`, `ripd` and `schema`.
- 12 rules: sensitive data basis, legitimate interest assessment, retention, international
  transfer mechanism, processor contracts, DPIA for high-risk operations, security measures,
  duplicate ids and DPO contact.
- Self-contained HTML report with risk matrix and open issues.
- Messages and outputs in Portuguese and English.
