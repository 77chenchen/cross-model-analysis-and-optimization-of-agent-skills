# Data release policy and unresolved raw-response choice

The committed release set contains de-identified metadata, frozen verifier
results, tool events, derived actions, and summary/manifest files for completed
pre-S7 r2 cohorts. Absolute local paths are replaced by `<REPO>` or `<HOME>`;
provider URLs, environment values, headers, and credentials are not exported.
S7 is excluded until its locked batch and formal analysis are complete.

Full raw responses are **not committed by default**. They can contain provider
reasoning fields, repeat task/code text, retain local paths, and are much larger
than derived trajectories. The owner must choose one release treatment:

1. **Recommended: do not release raw responses.** Publish the sanitized event
   and action streams plus hashes/counts, and document that raw responses are
   retained privately for audit.
2. Create a separately scrubbed compressed archive attached to a release, with
   its SHA-256 and a data dictionary. Keep it outside ordinary Git history.
3. Store a scrubbed archive in Git LFS. This preserves repository association
   but adds hosting/quota requirements and does not remove privacy review.

No option is executed automatically. Repository visibility and the final
license are also owner decisions.
