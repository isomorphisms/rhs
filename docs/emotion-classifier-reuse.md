# Syllabus emotion classifier reuse

Reference corpus: `bl4ckb4ll/syllabus/poetry/emotions/`.

The Syllabus emotion index is a multi-label reference graph. Canonical works are stored once; symbolic links under emotion directories assert label membership. The initial labels are Anger; Anxiety & Insecurity; Blame & Guilt; Boredom; Disappointment; Gratitude; Grief; Humor; Joy & Contentment; Melancholy & Despair; Optimism; Passion.

## Planned RHS use

For classifier experiments, treat a model-produced set of emotion labels as candidate output and the symlink-derived label set as the reference/oracle. RHS verification can then check the produced right-hand-side classification against the known memberships without modifying the reference corpus.

The comparison must be multi-label: missing labels and extra labels are distinct failures. Later experiments may use softer scores, but exact set equality should remain available as the simplest acceptance contract.

Training and evaluation must split on canonical works rather than symlink entries, and provenance should identify whether a reference edge was human-entered, imported from an external taxonomy, or later corrected.

Poetry is the seed corpus, not a permanent domain restriction. The same label relation is intended to classify other kinds of repository material later.

This note records planned reuse only; it does not add a classifier or training path yet.
