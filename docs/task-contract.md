# Task Contract: Multi-threaded GSim Optimization

- **Task name**: `gsim-32t-verilator-parity`
- **Objective**: Transform GSim from a high-performance sparse-evaluation single-thread RTL simulator into a multi-threaded simulator whose 32-thread performance is comparable to 32-thread Verilator on representative RTL designs.
- **Inputs**: GSim source tree, representative RTL designs, existing single-thread GSim outputs, Verilator 32-thread benchmark results, and `skills/mtwiki` domain references.
- **Outputs**: Candidate GSim implementation, correctness evidence, benchmark rows, profiling reports, and a promotion/rejection decision.
- **Correctness requirements**: Multi-threaded output must match the single-thread GSim reference bit-for-bit for all declared regression designs. Event ordering changes are allowed only when they preserve RTL-visible behavior.
- **Performance target**: 32-thread GSim runtime should reach parity with 32-thread Verilator for the declared benchmark set. Intermediate candidates may be promoted only when they improve the active baseline without correctness regressions.
- **Allowed implementation approaches**: static partitioning, over-decomposition, dynamic scheduling, work stealing, per-thread buffers, lock-free or low-contention queues, cache-line padding, NUMA-aware allocation, SIMD-friendly data layout, compiler flag tuning, and generated-code restructuring.
- **Constraints**: Prefer C++17-compatible changes unless the implementation workspace declares a newer standard. Do not add heavyweight external dependencies without explicit approval. Keep the workflow repository separate from generated artifacts.
- **Validation command**: Fill in inside the implementation workspace. It must include single-thread vs multi-thread trace/output comparison.
- **Evaluation command**: Fill in inside the implementation workspace. It must measure at least 1, 2, 4, 8, 16, and 32 threads when feasible.
- **Promotion criteria**: All validation passes; target benchmark improves versus parent baseline; profiling evidence identifies the reason for the change; `benchmark.csv` and `candidates.jsonl` are updated.
- **Rejection criteria**: Correctness mismatch, non-reproducible benchmark, statistically insignificant improvement with added complexity, slower parent comparison, or evidence showing the candidate optimizes a non-dominant bottleneck.
