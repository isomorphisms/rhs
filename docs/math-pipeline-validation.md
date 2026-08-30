# Exact theorem-aware pipeline validation

RHS consumes two observations produced from the same source input:

1. `EDRIC_MATH_ONE_STEP` is emitted only after the Idriç front end has parsed,
   elaborated, resolved its bounded mathematical obligations, and core-checked
   the result.
2. `MATH_BACKEND_EXECUTION` binds the exact artifact hash to a backend plan,
   generated target artifact, execution stage, and observed values.

`math_pipeline_validation.py` compares those observations with an independent
exact oracle.  It does not parse Idriç, perform theorem lookup, or lower a
mathematical operation.  This keeps RHS on the validation side of the boundary.

The canonical hostile fixture is genuinely 128-dimensional.  Its last
coordinate (zero-based index 127) is nonzero:

```text
x   = (3,  4, 12, 0, ..., 0,  9) : Vector R128
phi = (5, -2,  7, 0, ..., 0, 11) : Covector R128
y   = (5, -2,  7, 0, ..., 0, 11) : Vector R128
```

RHS requires the compiler artifact to distinguish `phi` from `y`, even though
their coordinates are equal.  The same-input trace is fixed at sixteen steps:
contraction; `x·x`, `x·y`, and squared norm; `Hx`, `Hy`, `H²x`, and the
reflected dot; `Gx`, `Gy`, `G²x`, `G³x`, `G⁴x`, and the rotated dot; then `G`
acting on the exact basis point `e128` of `S^127` and its squared norm.  Every
scalar and vector result is compared coordinate-for-coordinate with the exact
oracle.

Certificates are evidence-bearing records rather than labels.  Every record
must identify its goal, generator, reason, generated ordinary term, and
successful core check.  Unification records expose the resolved indices;
named-theorem records expose the theorem, typed hypotheses, and
`result=solved`.  Unknown trace vocabulary fails closed.

Hostile candidates have separate receipts so a backend cannot fabricate
compiler-negative evidence in its positive execution receipt.  Every hostile
receipt binds the exact `.idric` bytes; backend-owned cases additionally bind
the rejected one-step artifact or pseudo-ISA bytes.  RHS requires one exact
`FAIL / diagnostic=E_*` at the first boundary and dependency-blocked `SKIP`
rows afterward.

A fragment mock must say
`hardware_execution = SKIP` and `host_semantic_execution = PASS`; RHS will
reject a receipt that renames host interpretation as hardware execution.  An
x86 receipt must bind a generated ELF hash and record
`native_execution = PASS` while structurally proving that RefC, a host C
compiler, assembler, linker, and libc were absent from the generation path.

Run the exact self-tests with:

```text
python3 -m unittest -v test_math_pipeline_validation.py
```

The command-line validator takes the checked artifact, positive execution
receipt, and hostile-receipt directory in that order.
