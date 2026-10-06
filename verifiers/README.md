# Verifier protocol

Each verifier emits:

```json
{"passed": true, "checks": {}, "error": null}
```

Before a verifier is admitted, record three sanity cases:

1. a fully correct result must pass;
2. an obviously incorrect result must fail;
3. a superficially plausible shortcut or gaming attempt must fail.

The verifier package is copied into the workspace only after the agent ends, or executed from an external immutable location. Agent-authored tests and self-reported completion never determine benchmark success.
