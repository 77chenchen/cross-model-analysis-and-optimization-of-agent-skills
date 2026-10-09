# L3b descriptive results

This is a dev-validate-only, small-sample descriptive report. It does not claim that L3b is effective.

## dev_validate/baseline

Runs: 36; provider errors: 0; outcomes: {'empty_termination': 20, 'max_steps_reached': 7, 'pass': 8, 'verifier_fail': 1}.

Pass excluding provider errors: 0.222 (Wilson 95% [0.11716331975796668, 0.38084702946117704]).
Max-step reached: 0.194 (Wilson 95% [0.09753095418928912, 0.350280429951769]).
Mean partial score: 0.7990196078431373; mean seed-relative partial delta: 0.696078431372549; positive-delta frequency: 0.8823529411764706 (Wilson 95% [0.7337915722962867, 0.9532855333511756]).

## dev_validate/l3b

Runs: 36; provider errors: 0; outcomes: {'empty_termination': 11, 'max_steps_reached': 5, 'pass': 17, 'timeout': 1, 'verifier_fail': 2}.

Pass excluding provider errors: 0.472 (Wilson 95% [0.3198604151517942, 0.62994061977012]).
Max-step reached: 0.139 (Wilson 95% [0.06081815009132971, 0.28659530389355725]).
Mean partial score: 0.8872549019607843; mean seed-relative partial delta: 0.7843137254901961; positive-delta frequency: 0.9411764705882353 (Wilson 95% [0.809063930957195, 0.9837173447898768]).

## Mechanism activation

L3b reminders triggered in 12/36 assigned runs (Wilson 95% [0.202146188243056, 0.49666002128843023]). Among triggered runs, post-trigger validation was 0.9166666666666666, partial increase was 1.0, and final pass was 0.16666666666666666. The mechanism is observable only where triggered; samples are small.
