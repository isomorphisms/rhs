# Geometry semantic-validation cases

Cross-repository geometry inventory:
[isomorphisms/Idric issue #108, “Inventory geometric carriers: spheres, projective spaces, quaternions, and orthogonal transforms”](https://github.com/isomorphisms/Idric/issues/108).

RHS should use the rotation, sphere, reflection, and hyperplane work as
controlled semantic-validation cases: do human-facing names and descriptions
agree with independently observed behavior?

RHS is not the canonical geometry library. It must not infer meaning from
storage layout, compiler IR, matrices, tuples, or byte encodings. The source
projects own the semantic objects and representation boundaries. RHS consumes
declared behavior and independently checkable fixtures.

## Positive and negative controls

Build small cases around claims such as:

- normalization maps a nonzero vector in `R^n` to a point of `S^(n-1)`;
- the compact octahedral direction codec represents `S^2`, not a general
  `S^3` quaternion or `SO(3)` orientation;
- encode/decode is an approximate quantized round trip, not an exact inverse;
- a Givens/plane rotation preserves the norm and zeroes the named coordinate;
- a Householder map is a reflection, while a product of two reflections may be
  a proper rotation;
- unit quaternions `q` and `-q` represent the same element of `SO(3)`;
- an affine hyperplane is represented by `n·x + b = 0`, with representation
  scale equivalence distinct from an oriented classifier's positive side;
- a change of orthonormal coordinates preserves geometric classification when
  the point and hyperplane are transformed consistently.

For each case, keep the declared human-facing claim, source revision, input,
observed output, tolerance or exactness rule, and independently justified
expected behavior separate. Include dishonest or misleading names as negative
controls instead of letting a model's agreement define ground truth.

## Existing bounded executable slice

[`vector_transforms.py`](../vector_transforms.py) already supplies two exact
repository-local operations: reflection through a coordinate hyperplane and
rotation by quarter turns in a selected coordinate plane.
[`test_vector_transforms.py`](../test_vector_transforms.py) checks the selected
coordinate behavior, reflection involution, rotation direction, four-turn
identity, squared-length preservation, and invalid coordinate inputs.

That fixture is useful precisely because its claim is narrow. It does not
establish arbitrary-angle Givens rotations, general Householder maps, quaternion
semantics, compact-direction encoding, affine-hyperplane scale or orientation,
or coordinate-invariant classification. Those cases still require fixtures from
their semantic owners. No model or classifier is ground truth for this slice.

## Project links

- [Idriç semantic inventory](https://github.com/isomorphisms/Idric/issues/108)
- [Android sensor/direction/orientation boundary](https://github.com/Ashtray-Archer/utilities-android-phone-user/issues/70)
- [constrained compact-direction follower](https://github.com/isomorphisms/idric-embedded/pull/13)
- [Coxeter reflection/rotation carriers](https://github.com/isomorphismes/coxeter/issues/8)
- [shader transform lowering](https://github.com/isomorphisms/idris-shader-backend/issues/32)
- [Pensieve embeddings and hyperplanes](https://github.com/isomorphisms/ib/issues/80)
- [Cockswain activation/hyperplane contracts](https://github.com/isomorphisms/cockswain/issues/17)
- [Fulton representation carriers](https://github.com/walnut-burgundy/fulton/issues/7)
- [shared Givens receipt policy](https://github.com/isomorphisms/ai-ci/issues/29)

The first useful RHS slice is a small positive/negative fixture set against
stable named operations, not another implementation of the underlying
mathematics.
