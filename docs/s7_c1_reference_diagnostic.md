# S7 C1 explicit-reference diagnostic

This local-only diagnostic covers usable S7 C1 runs for qwen3.8:27b, qwen3-coder-next, and llama3.1:8b. It does not call a provider or judge. The locked C1 protocol was delivered inline in the serialized request, rather than as a workspace skill file or an `open_skill` tool. Consequently, a `read_file` action is not evidence that the supplied protocol was opened.

| Model | Usable C1 runs | Locked-parser explicit references | Raw content marker | Raw reasoning marker | Any raw marker | `read_file` path containing `skill` |
|---|---:|---:|---:|---:|---:|---:|
| qwen3.8:27b | 54 | 0 | 0 | 0 | 0 | 10 |
| qwen3-coder-next | 54 | 0 | 0 | 0 | 0 | 0 |
| llama3.1:8b | 54 | 1 | 1 | 0 | 1 | 0 |

Markers are the case-insensitive literal strings `skill protocol`, `skill A`, `skill B`, or `skill C`, scanned over locally stored `content`, `reasoning`, and `reasoning_content` fields. The ten qwen3.8 path matches are ordinary workspace file paths containing the lexical substring `skill`; because the protocol is not materialized as such a file, they do not establish protocol opening. The near-zero explicit-reference rate therefore reflects the inline delivery and a narrow mention-based parser; it should not be read as evidence that a model did not receive the protocol or did not execute any of its behaviors.
