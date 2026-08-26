# Ithon name-vector work

The LHS/name-vector probe belongs in Ithon (`.pi`). The existing Python prototype is not the intended implementation language.

Target boundary for the replacement:

- exact literal LHS identifier text in
- one or more code-oriented embedding providers
- raw vector coordinates out, preserving provider identity and dimensions
- no RHS comparison or semantic verdict at this stage

Python may exist only as optional foreign-runtime glue for a model implementation that cannot yet be called directly from Ithon.
