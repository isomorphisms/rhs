# Hungarian-notation vector controls

This directory gives the RHS name-verification work a controlled experiment in
which the intended name transformation is known before any embedding model is
run.

## Historical fixture

Microsoft's Win32 coding-conventions documentation distinguishes the original
semantic form of Hungarian notation from the later type-encoding form. It gives
these examples:

- `i`: index
- `cb`: count/size in bytes
- `rw`: row number
- `col`: column number
- `dw`: `DWORD` (type-oriented form)
- `w`: `WORD` (type-oriented form)

Source, checked 2026-08-26:

https://learn.microsoft.com/en-us/windows/win32/learnwin32/windows-coding-conventions

`fixtures.py` records those prefixes as explicit primitives and concatenates
them with several stems. For example:

    Buffer  -> cbBuffer
    Packet  -> cbPacket
    Flags   -> dwFlags

The ground truth for an edge is the declared operation "add the `cb` byte-count
prefix", "add the `dw` DWORD prefix", and so on. The experiment does not ask a
model to invent that label.

## Exact capitalization control

The synthetic four-name control is deliberately even simpler:

    aBcd -> aBcD
    ABcd -> ABcD

Define, inside one fixed model and one fixed pooling rule,

    Delta_D(a) = E(aBcD) - E(aBcd)
    Delta_D(A) = E(ABcD) - E(ABcd)

Both edges have the declared meaning **capitalize the final D/d component**.
The first check is therefore whether `cos(Delta_D(a), Delta_D(A))` is close to
1.

The same square tests the independent leading A/a capitalization direction.
This `aBcd` cube is a synthetic control, not a claim that these four strings are
historical Hungarian notation.

## What gets scored

For every declared facet, `probe.py`:

1. embeds each distinct identifier once;
2. computes every edge as `on - off`;
3. measures whether the same facet points in a similar direction in other
   contexts;
4. builds leave-one-edge-out facet prototypes;
5. asks which declared facet best matches each held-out difference vector.

The reported `facet_accuracy` is therefore identification accuracy, not a vague
similarity score. Each facet also reports its leave-one-out directional
alignment and the number of zero edges.

A zero edge matters. For example, a model/tokenizer that removes case
distinctions cannot support a meaningful D-d direction; the probe reports that
as zero/undefined instead of pretending the vector has semantic content.

No vector coordinates are compared across different models. A direction is
only labeled inside the model/layer/pooling space that produced it.

## Deterministic tests

The ordinary unit tests do not download models:

    python -m unittest tests.hungarian_notation.test_probe

They use an exact fixture oracle and an intentionally case-insensitive model to
verify both success and failure behavior.

## Hugging Face comparison

The optional runner uses the same `text -> vector` boundary as the existing RHS
name-vector code. It mean-pools the last hidden state under the attention mask
for every model so the measurement rule is held fixed.

Default comparison set:

- `microsoft/codebert-base`
- `huggingface/CodeBERTa-small-v1`
- `sentence-transformers/all-MiniLM-L6-v2`
- `bert-base-cased`
- `bert-base-uncased`

Run:

    python -m tests.hungarian_notation.run_huggingface

Or select models explicitly:

    python -m tests.hungarian_notation.run_huggingface \
        --model microsoft/codebert-base \
        --model bert-base-cased

`--include-vectors` emits the labeled prototype and individual difference
vectors as JSON. By default the report omits thousands of raw coordinates and
keeps the alignment, norms, labels, and classification results.

The runner stores model IDs only. It does not redistribute model weights; each
model is downloaded under its own Hugging Face terms when the optional
experiment is run.
