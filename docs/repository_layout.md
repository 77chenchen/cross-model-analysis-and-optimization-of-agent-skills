# Repository layout

- `analysis/`: read-only, versioned analysis, export, table, and figure code.
- `config/`: frozen protocols, controls, schedules, and execution locks.
- `data/`: committed summaries, blinded annotations, sanitized release data,
  and local ignored raw runs.
- `docs/`: protocols, errata, diagnostics, case studies, and stage reports.
- `figures/`: pre-S7 PNG/SVG exhibits and their CSV plotting data.
- `harness/`: runners, verifiers' invocation layer, and historical diagnostics.
- `metadata/`: run schemas.
- `results/tables/`: reproducible Markdown and CSV tables.
- `skills/`: frozen v0/v1 skill text.
- `tasks/`: frozen pilot and formal task assets plus admission records.
- `tests/`: unit and integration checks.
- `verifiers/`: external verifier implementation and contracts.

Raw run directories and provider responses are local/ignored. The release
export combines de-identified dev records under `data/release/`; S7 is not
exported while it is running.
