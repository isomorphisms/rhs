CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Wpedantic -O2

.PHONY: all check clean

all: glyph_bytes

glyph_bytes: glyph_bytes.c
	$(CC) $(CFLAGS) -o $@ $<

glyph_bytes.actual.txt: glyph_bytes
	./glyph_bytes > $@

check: glyph_bytes.actual.txt glyph_bytes.expected.txt
	cmp glyph_bytes.expected.txt glyph_bytes.actual.txt

clean:
	rm -f glyph_bytes glyph_bytes.actual.txt
