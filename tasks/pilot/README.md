# Pilot pool

This pool has 12 candidate tasks: six Skill A code-modification tasks and six Skill B file/data tasks. Every candidate must receive an immutable task template and an external verifier with positive, negative, and shortcut sanity cases before it can be run.

The first admission batch is A01--A04, adapted from the legacy tasks but rebuilt so the agent cannot modify verifier-owned tests. The remaining eight candidates are intentionally not runnable yet; they are task-design inventory, not experimental data.
