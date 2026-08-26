# Keyboard glyph bytes and semantic-vector experiments

This branch makes the glyph discussion inspectable at the byte level before assigning learned meanings to it.

`glyph_bytes.c` starts from numeric Unicode scalar values, encodes UTF-8 itself, and then uses `printf` to print the resulting character. Every output line therefore shows three things together:

    U+25AE bytes=E2,96,AE glyph=[▮] ...

That makes it easy for a human to see the glyph and for deterministic code (`grep`, `cmp`, a small parser) to see exactly which scalar value and bytes produced it.

## What is inventoried

The `software-keyboard` section is the union of Unicode scalar values occurring in the current button/token strings in `utilities-android-phone-user`:

- Punctuation—minimal
- Punctuation—extended
- Programming
- Mathematics
- Regex
- Unix terminal
- Programming punctuation
- Blackletter
- Extended border

Snapshot: `isomorphisms/utilities-android-phone-user` main at `9980f9ab3be0e7c2190531656330d570761cb770`, source `math-characters/idric/UnicodePicker.idric`.

The Extended border layout contains the complete Unicode Box Drawing block U+2500 through U+257F, so the fixture prints every box-drawing code point.

It also records candidates from the programmers-keyboard discussion, pinned here to `isomorphisms/programmers-keyboard` main at `3d88a045f6134da19a340de0de30e7a6f72c3915`, including `|`, `›`, `▷`, composition, arrows, and the newer vertical-marker candidates.

Controls are explicit too: TAB, LF, CR, and both LF and CRLF sequences. The fixture puts stdout into binary mode on Windows so running the test does not silently turn the fixture's LF bytes into CRLF.

`glyph_bytes.expected.txt` is the output of compiling and running this exact C program. `make check` rebuilds the program, runs it, and byte-compares the output.

## Propagation rule

This fixture is an observer and experiment surface, not the only source of keyboard layout truth. When a glyph becomes an accepted key or text convention, the intended propagation is:

1. put it in the appropriate programmers/hardware keyboard layout;
2. make the phone/software keyboard aware of it;
3. add its numeric scalar here and regenerate the byte fixture;
4. only then attach or measure semantic vectors against the explicit glyph identity.

That keeps the physical keyboard, software keyboard, and equality/vector experiments cross-checkable without requiring them to be identical products.

The current discussion set deliberately includes `▮`, `│`, `┃`, `║`, the flared-top box characters, `▌`, `█`, `❘`, `›`, `▷`, and `←`/`→`. Inclusion here means “track and test this candidate,” not “Unicode or every programming language now has this meaning.”

## Why this exists

Existing embedding models learned from prior text and prior code. That is evidence about historical usage, not a law saying what a glyph must mean in this project.

We may deliberately establish new local conventions and then measure them.

A current example is:

- `│` U+2502: candidate for structural continuation.
- `▮` U+25AE BLACK VERTICAL RECTANGLE: candidate for human-readable commentary, warning prose, or an email-reply-like margin bar. It is intentionally visually unlike ordinary source punctuation.
- `|` U+007C: keep visible as the heavily overloaded historical ASCII vertical line rather than pretending it has only one meaning.

The point is not to redefine Unicode's official character names. The point is to make our project-local use explicit, reproducible, searchable, and eventually learnable.

A ragged-text producer could therefore emit something like:

    vector: [...]
    type: Float32 × n
    warning:
    ▮ human-readable explanation continues here
    ▮ and can occupy several physical lines

The vector, type information, and warning remain ordinary text. Newlines and spaces retain their ordinary human value. A consumer can be sophisticated, or it can be as simple as `grep '▮'`.

## Vector hypothesis: arrows and an opposing direction

A useful test case is `←` versus `→`.

The hypothesis is not that some pre-existing model is guaranteed to contain a magic “before/after” coordinate. It is that, after fixing a model/layer/tokenization and supplying sufficiently controlled contexts, there may be a stable **direction or low-dimensional subspace** that distinguishes paired ideas such as:

    before / after
    input / output
    assignment-to / flow-from
    ← / →

This is the same kind of relational question that made old embedding arithmetic such as `king - queen ≈ man - woman` interesting. The useful object is the repeatable difference relation, not the slogan.

Tests should therefore:

1. Collect vectors for paired, controlled contexts.
2. Compute the difference vectors for `←` and `→` (and other pairs).
3. Test the direction on held-out contexts rather than only the examples used to discover it.
4. Check whether the sign reverses when the relation reverses.
5. Compare across model versions/layers so we know what is actually stable.
6. Only after that, inspect which coordinates carry the relation.

If, for one fixed representation, dimensions such as 697, 10,001, and 400,003 repeatedly carry coefficients for the same relation, record that empirical fact. Do not assume those coordinate numbers transfer to another model.

A basis transform is then a real possibility. If a stable semantic subspace exists, PCA/SVD, an orthogonal rotation, or another explicit transform could put “before/after” or “human comment / structural syntax” onto a cleaner axis. That would make the representation easier for us to inspect and possibly easier to assign manually.

The mathematical caution is important: individual raw dimensions have no invariant meaning merely because they have numbers. Rotating an embedding basis can preserve the relational geometry while moving the information to different coordinates. So this project should first establish **relations and subspaces**, and only then choose a convenient basis.

## Manually assigned vectors

`glyph_bytes.c` contains commented-out scaffolding for sparse, human-assigned target vectors. It is commented out on purpose.

For a glyph such as `▮`, we may eventually say: in *our* representation this is human-readable commentary / continuation, and explicitly assign or fit a vector for that meaning. That lets new usage enter the experiment without pretending historical training data already meant what we now want it to mean.

The emitted glyph bytes are the fixed observation boundary. Semantic vectors can change and be tested above that boundary.
