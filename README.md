# RHS

Functions should do what they say they do.

RHS is an empirical validation project for checking whether program names and
other human-facing claims agree with observed program behavior.  Its first job
is not to prove a programming language or type theory correct.  It is to build
controlled examples with known meanings, run candidate models or other
classifiers against them, and measure where the names and behavior agree or
mislead.

## First test cases

- Hungarian notation gives a small controlled naming experiment where the
  intended name transformation is known in advance.
- Adversarial and underhanded programs are useful negative cases: code whose
  surface presentation encourages an incorrect reading while its behavior does
  something else.
- Ordinary well-named code is needed as the corresponding positive control.

A model score is evidence about the model, not a proof about the program.
Ground truth should come from independently checkable behavior or fixtures
where the intended transformation is explicitly defined.

## Scope boundary

Compiler implementation and GCC pruning belong to ICK.  Speculative
proof/type-theory pipelines may be tested by RHS once their own assumptions are
validated, but they do not define the RHS baseline.

This repository was originally created as a fork of GCC.  The inherited GCC
source is historical scaffolding, not the intended RHS architecture, and should
be removed as repository cleanup once any useful compiler work has been
preserved in ICK.
