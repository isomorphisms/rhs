# Underhanded C: small, checkable counterexamples

This is an RHS corpus, not a compiler implementation or a proof of a type
system. Start with independently checkable differences between an apparent
contract and actual behavior. No model or RHS detector has been evaluated here.

These are newly written **mechanism reductions**, not imported contest source
or reproductions of complete winning entries. The judges' accounts below supply
provenance. Deliberately faulty and corrected variants share the same ordinary
control and adversarial property test. Keep both variants.

## First eight cases

| File | Contest provenance | Trigger and violated property |
| --- | --- | --- |
| `01_xor_swap_alias.c` | 2007, Wagner/Biondi runners-up [S07] | XOR exchange with aliased arguments erases 71. Self-exchange must preserve it. |
| `02_macro_precedence.c` | 2008, Linus Akesson, third place [S08] | Equivalent comparisons produce pixel widths 3 and 6 because an argument lacks parentheses. |
| `03_redaction_width.c` | 2008, John Meacham, winner [S08] | Digit replacement leaves `7` as `0` and `255` as `000`: black pixels, different observable token lengths. |
| `04_bitwise_truth.c` | 2013, Jon Szymaniak, discussed entry [S13] | Nonzero comparison results 2 and 4 disappear under bitwise AND. |
| `05_equality_identity.c` | 2013, Simon Nicolussi, discussed entry [S13] | Equal IDs suppress copying between distinct records with different distances. |
| `06_macro_repeated_effect.c` | 2014, Karen Pease, winner component [S14] | A leap-year macro evaluates an auditing argument three times instead of once. |
| `07_nan_fail_open.c` | 2015, NaN submission family [S15] | Negating a failed lower-bound comparison accepts NaN. |
| `08_error_flag_copy.c` | 2015, Michael Dunphy, discussed entry [S15] | Validation changes a parameter copy; the caller's error flag stays clear. |

The reductions avoid deliberate memory corruption and undefined behavior. Case
02 stops at the width disagreement rather than reading past an allocation.
Case 04 uses supplied integer comparison results, not subtraction of unrelated
pointers. Case 06 isolates repeated evaluation, not the full winner's overwrite
chain. Case 07 supplies NaN directly to isolate the gate; it does **not** reproduce
an entry's input-to-NaN path. Case 08 tests only error propagation.

The redaction contract compares serialized outputs for two private values with
identical public context, not just how those outputs render. The equality case
requires copying record state; equality of one key is not equality of the whole
record, and neither establishes identity of storage.

For NaN, ordered comparisons such as `<` and `>=` are false under the semantics
tested here, while `NaN != NaN` is true. Do not generalize the judges' shorthand
into a claim that every comparison is false. The corrected gate requires a
finite score. Unsupported NaN semantics return 77, not a passing result.

## Run

Python 3.10 or later and a C11 compiler are sufficient. There are no Python
packages, network requests, full GCC builds, or external data dependencies.
From the repository root:

```sh
python3 'underhanded C/run.py' --cc gcc --cc clang
```

With one compiler, including a compiler executable supplied through `CC`:

```sh
python3 'underhanded C/run.py' --cc cc --opt 2
```

The runner defaults to `-O0` and `-O2`. Each compiler/optimization pair builds
every case twice, with `USE_CORRECTED=0` and `USE_CORRECTED=1`. It requires:

- the faulty variant to pass its ordinary control, then exit 1 with its exact
  `CONTRACT_FAIL <case>` line;
- the corrected variant to pass the same control and property, then exit 0
  with its exact `CONTRACT_PASS <case>` line.

A crash, timeout, compilation failure, different diagnostic, or broken ordinary
control is a failure, not successful detection. Unsupported executions are
recorded separately and make the runner exit 3. Failures make it exit 1.
Transient executables and the JSON receipt live under `_/`; executables are
removed after the run. `--receipt PATH` selects another receipt destination.
Compiler arguments are explicit and stored in the receipt; `--cc` is one
executable, not an evaluated shell command. Fast-math flags are not enabled.

Warnings are enabled and recorded, not suppressed or promoted to errors. Some
reductions already attract ordinary compiler warnings. This is not a claim
that they evade existing diagnostics.

## What would count as foiling a trick?

Today's result establishes the counterexample and its corrected control. It
does not establish autonomous detection, novel defenses, or general correctness.
A future candidate must diagnose the violated property in the faulty variant
without rejecting the corrected one. Keep its predictions separate from the
independent runtime oracle and report false positives as well as detections.

Possible tests include alias-aware contracts (01), macro hygiene and effect
counts (02/06), noninterference of redacted output (03), Boolean versus bit-mask
results (04), distinct equality relations (05), finite-number requirements (07),
and explicit error-return or output contracts (08). These are proposed tests,
not accepted RHS capabilities or assumptions that a speculative theory is sound.

The filenames, comments, `USE_CORRECTED` switch and expected diagnostic reveal
the labels. Do not feed those clues to a classifier and report the resulting
score as semantic understanding. Prepare label-free candidate inputs, renamed
and structural variants, and held-out cases before evaluating a detector.

## Larger cases to add later

| Provenance | Mechanism to investigate; not executable coverage here |
| --- | --- |
| 2013 winner, Alex Olson [S13] | Conflicting `int *` / `long *` declarations across source files; wider writes overwrite neighboring state. |
| 2013, Dan Jackson / Gaetan Leurent [S13] | `abs(INT_MIN)` and optimizations after undefined behavior. Do not assert a portable runtime result. |
| 2014 winner, Karen Pease [S14] | Reused `localtime` storage plus repeated auditing, malformed macro expansion and buffer overflow. |
| 2015 winner, Linus Akesson [S15A] | Different source files disagree about `float_t`, reading storage with the wrong floating-point layout. |
| 2015, Stephen Dolan [S15] | Small residuals vanish during floating-point accumulation before the largest term is removed. |

The 2015 winner needs a multi-file fixture with explicit floating representation
and evaluation-mode checks: `float_t` is not universally `float`. Keep compiler
or linker diagnostics separate from runtime behavior. ABI- or undefined-behavior
cases need explicit platform conditions and must not turn crashes into wins.
Do not make the safe starter run execute an unreviewed historical program.

## Evidence and followers

`BASELINE.json` records the initial local compiler matrix, source-file SHA-256
hashes and pending follower targets. Its `source_manifest_sha256` identifies the
exact tested code artifact independently of the later publication commit.
Regenerate receipts when any source changes; the initial record is historical
then. A receipt is an evidence record, not a tamper-proof attestation.

Only local x86-64 Debian execution is claimed. Hetzner, GitHub Actions, ARMv7
phone and AArch64 tablet runtime runs remain pending at that same source
manifest. Follow the current shared runner policy for any later CI wiring;
this change does not add or alter workflows. No physical-device, compiler-
backend or model acceptance is implied.

## Primary sources

[S07]: https://www.underhanded-c.org/_page_id_16.html
[S08]: https://www.underhanded-c.org/_page_id_17.html
[S13]: https://www.underhanded-c.org/_page_id_25.html
[S14]: https://www.underhanded-c.org/_page_id_26.html
[S15]: https://www.underhanded-c.org/
[S15A]: https://www.underhanded-c.org/two.pdf

- [S07: official 2007 results][S07]
- [S08: official 2008 results][S08]
- [S13: official 2013 results][S13]
- [S14: official 2014 results][S14]
- [S15: official 2015 results][S15]
- [S15A: 2015 winner's own explanation][S15A]

Consulted 2026-09-11. Attribution distinguishes winners, runners-up, other
submissions and reduced components. Linked source publication is not assumed
to grant permission to mirror complete submissions; none are mirrored here.
