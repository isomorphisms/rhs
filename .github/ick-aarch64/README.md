# ICK AArch64 compiler artifact

This archive contains an experimental GCC/ICK C compiler hosted on x86-64
Ubuntu 24.04 and targeting little-endian AArch64 GNU/Linux objects.  It is
qualified for the narrow role needed by Wegert: compile header-free leaf C
translation units with `-fPIC`, then let Android NDK r29 Clang/lld perform the
final Android API 26 link.

On Ubuntu 24.04, install `binutils-aarch64-linux-gnu`, `libgmp10`, `libmpfr6`,
`libmpc3`, `libisl23`, and `libzstd1` before invoking `bin/ick-aarch64`.  The
archive deliberately does not bundle binutils, a target libc/sysroot, or
target runtime libraries.  Use this compiler for `-S` or `-c`, not as the
Android linker driver.

Floating `_Complex` values use ICK's physical polar representation.  Keep
every `_Complex` value and operation inside an ICK-compiled translation unit.
The boundary to NDK Clang/C++ must contain only ordinary scalar and pointer or
array parameters; the ICK `_Complex` calling and object ABI is not compatible
with Clang's Cartesian representation.

This draft is qualified only for the exercised leaf-object pattern.  The
focused suite covers direct returns of complex constants and lvalue stores
through `__real__` or `__imag__` on nonvolatile objects.  It also covers
compile-time conversion of semantic complex constants to complete physical
object bytes and of complete physical object images back to semantic
components.  Partial or volatile bytewise views of complex storage, and calls
to external functions that accept or return `_Complex`, still have
representation gaps.  The Wegert fixture uses none of those operations; they
remain blockers to treating this as a general maintained `_Complex`
implementation.

This qualification covers finite Cartesian inputs only.  ICK's two-word
polar representation does not preserve every ISO C `_Complex` distinction
involving infinities, NaNs, or signed-zero quadrants; code needing those cases
must handle them explicitly at the scalar boundary.

The workflow verifies a relocated archive, executes the focused polar-storage
and radial floor/ceil tests under qemu-aarch64, and links an ICK-built PIC
object into an Android arm64-v8a shared library with NDK
`29.0.14206865`.  That link gate does not qualify NDK headers, C++ interop,
TLS, sanitizers, LTO, long-double ABI details, or arbitrary Android platform
APIs.

The Actions artifact is short-lived qualification output.  A consumer should
use an immutable release archive and verify its published SHA-256 checksum.
