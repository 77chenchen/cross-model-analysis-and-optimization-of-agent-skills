# A04 known task defect

`task.md` requires a deterministic topological order in which “tied ready
nodes are alphabetical.” For the verifier input
`{'app':['api','ui'], 'api':['db'], 'ui':[], 'db':[]}`, a globally alphabetical
ready-node rule produces `['db', 'api', 'ui', 'app']`: after `db` is removed,
both `api` and `ui` are ready and `api` sorts first.

The frozen verifier instead requires `['db', 'ui', 'api', 'app']`. Thus its
`order` check encodes a tie-breaking policy not stated by the task and
inconsistent with the stated alphabetical policy. `value_only` and `cycle`
are stated by the task; the exact order check is the known defect.

This is recorded without changing the frozen task, seed, fixture, or verifier.
It must not motivate a new intervention from `dev_validate` trajectories.
