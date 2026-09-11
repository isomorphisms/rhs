# Underhanded C controls

The Underhanded C Contest is almost a direct adversarial benchmark for RHS: the
contest asks for source that appears clear, innocent, and straightforward while
its actual behavior violates the apparent function.

This directory starts conservatively with a manifest of independently described
cases from the official contest pages. It does **not** copy contestant source.
Before source is mirrored here, record its provenance and redistribution terms.

Each case separates:

- the apparent task or claim a reviewer is encouraged to believe;
- the documented hidden behavior;
- the kind of semantic mismatch RHS should try to detect;
- the authoritative contest page that establishes the ground truth.

These records are negative controls. A useful benchmark also needs ordinary
implementations of the same apparent tasks that do not contain the documented
underhanded behavior, so a model cannot succeed merely by learning that every
fixture in this directory is bad.

The first cases intentionally span different failure modes: hidden dependence on
uninitialized state, misleading performance behavior, a security-sensitive API
or prototype mismatch, visually deceptive string handling, and validation code
whose type mismatch corrupts authorization state.
