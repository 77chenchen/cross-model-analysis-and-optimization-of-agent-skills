# S0 sampling-control probe

Date: 2026-10-07. The active execution path is Codex CLI with either the
ChatGPT provider or the SoC LaaS profile.

## Probe

The CLI was invoked in strict configuration mode with `temperature=0.5` and,
separately, `seed=12345`. Both invocations failed before any model request:

- `unknown configuration field temperature`
- `unknown configuration field seed`

Because this rejection happens in the shared CLI configuration parser, it is
an execution-path limitation for all six configured model IDs rather than a
per-model acceptance result. No claim is made about whether a provider's raw
API could accept these parameters through another client.

## Decision

The study requests temperature 0.5 and three fresh repetitions, but records
the effective temperature and seed as unknown/null with
`sampling_control: unsupported_by_cli` until the runner is replaced or extended
with a parameter-capable provider client. Legacy temp0 pilots are retained and
reported separately.
