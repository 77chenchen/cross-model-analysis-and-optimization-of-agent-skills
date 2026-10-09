# L3b revised descriptive analysis

Pre-registered metrics are retained separately. Everything below is post-hoc exploratory; Wilson intervals in the original report quantify single proportions only and are not condition-difference tests.

## Reconstructed outcomes and final-empty behavior

- baseline: reconstructed {'pass': 21, 'verifier_fail': 7, 'compile_error': 1, 'max_steps_reached': 7}; legacy {'empty_termination': 27, 'pass': 8, 'verifier_fail': 1}; final-empty rate 0.750; final-empty × pass {'empty_pass': 13, 'empty_nonpass': 14, 'nonempty_pass': 8, 'nonempty_nonpass': 1}.
- l3b: reconstructed {'pass': 23, 'timeout': 1, 'verifier_fail': 7, 'max_steps_reached': 5}; legacy {'empty_termination': 17, 'pass': 17, 'verifier_fail': 2}; final-empty rate 0.472; final-empty × pass {'empty_pass': 6, 'empty_nonpass': 11, 'nonempty_pass': 17, 'nonempty_nonpass': 2}.

Final-empty is now an independent behavioral indicator: abnormal termination is classified first, then compile/verifier outcome; legacy `empty_termination` remains for audit only.

## Post-call-32 write-only replay

Pre-32 terminal replay exactly matched final workspace in 46/51 checked runs; 5 mismatched. There were 9 baseline and 12 L3b A-layer candidates; 10 L3b increments were scoreable because one user-authorized verifier timeout had no final partial and one verifier result was unavailable. A-layer (>=32 calls) final_partial − partial_at_32: baseline negative control mean 0.0 (n=9), L3b mean 0.058333333333333334 (n=10). Task-paired bootstrap: {'task_pairs': 4, 'mean_difference_l3b_minus_baseline': 0.043402777777777776, 'paired_bootstrap_95': [0.0, 0.08680555555555555]}. `run_command` side effects are not replayed, so these increments are exploratory.
