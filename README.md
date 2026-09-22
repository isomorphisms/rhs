# RHS

Functions should do what they say they do.

RHS is an empirical validation project for checking whether program names and
other human-facing claims agree with observed program behavior. Its first job is
not to prove a programming language or type theory correct. It is to build
controlled examples with known meanings, run candidate models or other
classifiers against them, and measure where names, descriptions, and behavior
agree or mislead.

## First test cases

- `tests/hungarian_notation/` is the smallest controlled naming experiment: the
  intended name transformation is declared before a model is consulted.
- `tests/underhanded_c/` records adversarial programs whose apparent purpose and
  actual behavior are independently documented. These are negative controls for
  source-level semantic review.
- Ordinary well-named code is needed as the corresponding positive control.

A model score is evidence about the model, not a proof about the program.
Ground truth should come from independently checkable behavior or fixtures where
the intended transformation is explicitly defined.

## Scope boundary

Compiler implementation and GCC pruning belong to ICK. Speculative proof or
type-theory pipelines may be tested by RHS after their own assumptions are
validated, but they do not define the RHS baseline.

RHS began life as a fork of GCC. The inherited GCC working tree has been removed
from the current branch; its complete history remains in Git, and compiler work
that still matters is tracked in ICK.

## Current experiments

`semantic_equality.py` supplies the deliberately small same-input/two-sides
observation boundary. `equality_mocks.py` contains dishonest controls for testing
consumers. `vector_transforms.py` contains exact geometric utilities used by
some vector experiments. [`docs/geometry-semantic-validation.md`](docs/geometry-semantic-validation.md)
connects rotation, sphere, reflection, and hyperplane claims to controlled RHS
positive and negative cases. `keyboard-glyphs/` and `docs/` contain earlier
semantic fixtures that remain useful but do not define the architecture.
