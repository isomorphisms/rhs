/*
 * Byte-exact Unicode glyph inventory for the equality experiment.
 *
 * Unicode scalar values are stored numerically and UTF-8 is encoded here.
 * The visible glyph on each output line is printf'd from those encoded bytes.
 *
 * Software-keyboard snapshot:
 *   isomorphisms/utilities-android-phone-user
 *   9980f9ab3be0e7c2190531656330d570761cb770
 *   math-characters/idric/UnicodePicker.idric
 *
 * Related programmers-keyboard snapshot:
 *   isomorphisms/programmers-keyboard
 *   3d88a045f6134da19a340de0de30e7a6f72c3915
 */

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

struct discussed_glyph {
  uint32_t cp;
  const char *note;
};

static void make_stdout_binary(void)
{
#ifdef _WIN32
  /* Keep fixture newlines as LF instead of silently translating to CRLF. */
  (void)_setmode(_fileno(stdout), _O_BINARY);
#endif
}

static size_t utf8_encode(uint32_t cp, unsigned char out[4])
{
  if (cp <= 0x7Fu) {
    out[0] = (unsigned char)cp;
    return 1;
  }
  if (cp <= 0x7FFu) {
    out[0] = (unsigned char)(0xC0u | (cp >> 6));
    out[1] = (unsigned char)(0x80u | (cp & 0x3Fu));
    return 2;
  }
  if (cp >= 0xD800u && cp <= 0xDFFFu)
    return 0;
  if (cp <= 0xFFFFu) {
    out[0] = (unsigned char)(0xE0u | (cp >> 12));
    out[1] = (unsigned char)(0x80u | ((cp >> 6) & 0x3Fu));
    out[2] = (unsigned char)(0x80u | (cp & 0x3Fu));
    return 3;
  }
  if (cp <= 0x10FFFFu) {
    out[0] = (unsigned char)(0xF0u | (cp >> 18));
    out[1] = (unsigned char)(0x80u | ((cp >> 12) & 0x3Fu));
    out[2] = (unsigned char)(0x80u | ((cp >> 6) & 0x3Fu));
    out[3] = (unsigned char)(0x80u | (cp & 0x3Fu));
    return 4;
  }
  return 0;
}

static void print_encoded_bytes(const unsigned char *bytes, size_t n)
{
  size_t i;
  for (i = 0; i < n; ++i) {
    if (i != 0)
      printf(",");
    printf("%02X", (unsigned int)bytes[i]);
  }
}

static void print_visible(uint32_t cp, const unsigned char *bytes, size_t n)
{
  char utf8[5] = {0, 0, 0, 0, 0};

  if (cp == 0x0009u) { printf("<TAB>"); return; }
  if (cp == 0x000Au) { printf("<LF>"); return; }
  if (cp == 0x000Du) { printf("<CR>"); return; }
  if (cp == 0x0020u) { printf("<SPACE>"); return; }

  memcpy(utf8, bytes, n);
  utf8[n] = '\0';
  printf("%s", utf8);
}

/*
 * One deterministic line printer for controls, keyboard characters, new
 * glyph proposals, and 4-byte emoji.  The glyph is derived from cp.
 */
static void print_codepoint(uint32_t cp, const char *source, const char *note)
{
  unsigned char bytes[4];
  size_t n = utf8_encode(cp, bytes);

  if (n == 0) {
    printf("U+%04" PRIX32 " bytes=<invalid> glyph=[<invalid>] source=%s\n",
           cp, source);
    return;
  }

  printf("U+%04" PRIX32 " bytes=", cp);
  print_encoded_bytes(bytes, n);
  printf(" glyph=[");
  print_visible(cp, bytes, n);
  printf("] source=%s", source);
  if (note != NULL)
    printf(" note=\"%s\"", note);
  printf("\n");
}

static void print_sequence(const uint32_t *cps, size_t count,
                           const char *source, const char *note)
{
  size_t i;

  printf("sequence bytes=");
  for (i = 0; i < count; ++i) {
    unsigned char bytes[4];
    size_t n = utf8_encode(cps[i], bytes);
    if (i != 0)
      printf(",");
    print_encoded_bytes(bytes, n);
  }

  printf(" glyph=[");
  for (i = 0; i < count; ++i) {
    unsigned char bytes[4];
    size_t n = utf8_encode(cps[i], bytes);
    print_visible(cps[i], bytes, n);
  }
  printf("] source=%s note=\"%s\"\n", source, note);
}

/*
 * Unique Unicode scalars occurring in the current software keyboard button
 * and token strings: Punctuation-minimal, Punctuation-extended, Programming,
 * Mathematics, Regex, Unix terminal, Programming punctuation, Blackletter,
 * and Extended border.
 *
 * Extended border contains every scalar U+2500..U+257F, so this includes the
 * complete Unicode Box Drawing block.
 */
static const uint32_t keyboard_codepoints[] = {
  0x0020u, 0x0021u, 0x0022u, 0x0023u, 0x0024u, 0x0025u, 0x0026u, 0x0027u,
  0x0028u, 0x0029u, 0x002Au, 0x002Bu, 0x002Cu, 0x002Du, 0x002Eu, 0x002Fu,
  0x0030u, 0x0031u, 0x0039u, 0x003Au, 0x003Bu, 0x003Cu, 0x003Du, 0x003Eu,
  0x003Fu, 0x0040u, 0x0041u, 0x0042u, 0x0043u, 0x0044u, 0x0045u, 0x0046u,
  0x0047u, 0x0048u, 0x0049u, 0x004Bu, 0x004Cu, 0x004Du, 0x004Eu, 0x004Fu,
  0x0050u, 0x0051u, 0x0052u, 0x0053u, 0x0054u, 0x0055u, 0x0057u, 0x005Au,
  0x005Bu, 0x005Cu, 0x005Du, 0x005Eu, 0x005Fu, 0x0060u, 0x0061u, 0x0062u,
  0x0063u, 0x0064u, 0x0065u, 0x0066u, 0x0067u, 0x0068u, 0x0069u, 0x006Au,
  0x006Bu, 0x006Cu, 0x006Du, 0x006Eu, 0x006Fu, 0x0070u, 0x0071u, 0x0072u,
  0x0073u, 0x0074u, 0x0075u, 0x0077u, 0x0079u, 0x007Au, 0x007Bu, 0x007Cu,
  0x007Du, 0x007Eu, 0x00A1u, 0x00B0u, 0x00B1u, 0x00B4u, 0x00B7u, 0x00BFu,
  0x00C3u, 0x00CBu, 0x00D6u, 0x00D7u, 0x00DEu, 0x00DFu, 0x00E2u, 0x00E6u,
  0x00E7u, 0x00E9u, 0x00EFu, 0x00F0u, 0x00F1u, 0x00F6u, 0x00F7u, 0x00F8u,
  0x00F9u, 0x00FAu, 0x00FBu, 0x00FCu, 0x00FDu, 0x00FEu, 0x00FFu, 0x0100u,
  0x0101u, 0x010Bu, 0x0113u, 0x0117u, 0x012Bu, 0x014Du, 0x015Fu, 0x016Au,
  0x016Bu, 0x0177u, 0x0233u, 0x0325u, 0x039Bu, 0x03BAu, 0x03BBu, 0x03C0u,
  0x03C4u, 0x0407u, 0x1E0Du, 0x1E25u, 0x1E37u, 0x1E41u, 0x1E47u, 0x1E86u,
  0x1E8Fu, 0x1EF3u, 0x1EF5u, 0x1EF9u, 0x2013u, 0x2014u, 0x2022u, 0x2024u,
  0x2026u, 0x2032u, 0x2043u, 0x2109u, 0x2192u, 0x2200u, 0x2203u, 0x2204u,
  0x2208u, 0x2209u, 0x220Bu, 0x220Cu, 0x2212u, 0x2213u, 0x2218u, 0x221Au,
  0x221Eu, 0x2229u, 0x222Au, 0x2241u, 0x2248u, 0x2260u, 0x2264u, 0x2265u,
  0x2282u, 0x2284u, 0x2286u, 0x235Du, 0x23B6u, 0x23BAu, 0x23BBu, 0x23BCu,
  0x23BDu, 0x2500u, 0x2501u, 0x2502u, 0x2503u, 0x2504u, 0x2505u, 0x2506u,
  0x2507u, 0x2508u, 0x2509u, 0x250Au, 0x250Bu, 0x250Cu, 0x250Du, 0x250Eu,
  0x250Fu, 0x2510u, 0x2511u, 0x2512u, 0x2513u, 0x2514u, 0x2515u, 0x2516u,
  0x2517u, 0x2518u, 0x2519u, 0x251Au, 0x251Bu, 0x251Cu, 0x251Du, 0x251Eu,
  0x251Fu, 0x2520u, 0x2521u, 0x2522u, 0x2523u, 0x2524u, 0x2525u, 0x2526u,
  0x2527u, 0x2528u, 0x2529u, 0x252Au, 0x252Bu, 0x252Cu, 0x252Du, 0x252Eu,
  0x252Fu, 0x2530u, 0x2531u, 0x2532u, 0x2533u, 0x2534u, 0x2535u, 0x2536u,
  0x2537u, 0x2538u, 0x2539u, 0x253Au, 0x253Bu, 0x253Cu, 0x253Du, 0x253Eu,
  0x253Fu, 0x2540u, 0x2541u, 0x2542u, 0x2543u, 0x2544u, 0x2545u, 0x2546u,
  0x2547u, 0x2548u, 0x2549u, 0x254Au, 0x254Bu, 0x254Cu, 0x254Du, 0x254Eu,
  0x254Fu, 0x2550u, 0x2551u, 0x2552u, 0x2553u, 0x2554u, 0x2555u, 0x2556u,
  0x2557u, 0x2558u, 0x2559u, 0x255Au, 0x255Bu, 0x255Cu, 0x255Du, 0x255Eu,
  0x255Fu, 0x2560u, 0x2561u, 0x2562u, 0x2563u, 0x2564u, 0x2565u, 0x2566u,
  0x2567u, 0x2568u, 0x2569u, 0x256Au, 0x256Bu, 0x256Cu, 0x256Du, 0x256Eu,
  0x256Fu, 0x2570u, 0x2571u, 0x2572u, 0x2573u, 0x2574u, 0x2575u, 0x2576u,
  0x2577u, 0x2578u, 0x2579u, 0x257Au, 0x257Bu, 0x257Cu, 0x257Du, 0x257Eu,
  0x257Fu, 0x25A1u, 0x2605u, 0x2713u, 0x27E6u, 0x27E7u,
};

/*
 * Repetition with keyboard_codepoints is intentional.  These lines add the
 * proposed project-local semantic role under discussion.
 */
static const struct discussed_glyph discussion_codepoints[] = {
  {0x007Cu, "VERTICAL LINE — overloaded ASCII pipe"},
  {0x203Au, "SINGLE RIGHT-POINTING ANGLE QUOTATION MARK — piping/composition candidate from programmers-keyboard note"},
  {0x2190u, "LEFTWARDS ARROW — candidate before/input/assignment side of an opposing semantic relation"},
  {0x2192u, "RIGHTWARDS ARROW — candidate after/output/flow side of an opposing semantic relation"},
  {0x2218u, "RING OPERATOR — composition candidate"},
  {0x2502u, "BOX DRAWINGS LIGHT VERTICAL — structural continuation candidate"},
  {0x2503u, "BOX DRAWINGS HEAVY VERTICAL — strong structural continuation candidate"},
  {0x2533u, "BOX DRAWINGS HEAVY DOWN AND HORIZONTAL — flared-top pipe candidate"},
  {0x2551u, "BOX DRAWINGS DOUBLE VERTICAL — prominent continuation candidate"},
  {0x2565u, "BOX DRAWINGS DOWN DOUBLE AND HORIZONTAL SINGLE — flared-top pipe candidate"},
  {0x2566u, "BOX DRAWINGS DOUBLE DOWN AND HORIZONTAL — flared-top pipe candidate"},
  {0x2588u, "FULL BLOCK — very heavy vertical marker candidate"},
  {0x258Cu, "LEFT HALF BLOCK — heavy margin marker candidate"},
  {0x25AEu, "BLACK VERTICAL RECTANGLE — human-readable comment/annotation bar candidate"},
  {0x25B7u, "WHITE RIGHT-POINTING TRIANGLE — piping/composition candidate from programmers-keyboard note"},
  {0x2758u, "LIGHT VERTICAL BAR — ornamental vertical-bar candidate"},
  {0x1F600u, "GRINNING FACE — four-byte UTF-8/emoji smoke test"},
};

/*
 * Future manually assigned / empirically measured vector hook.
 *
 * Deliberately commented out.  Do not fill coefficients from vague historical
 * usage and then call them observations.
 *
 * struct vector_coordinate {
 *   size_t dimension;
 *   double coefficient;
 * };
 *
 * static const struct vector_coordinate black_vertical_rectangle_target[] = {
 *   {697,    0.0},   // replace with an explicit assigned/measured value
 *   {10001,  0.0},
 *   {400003, 0.0},
 * };
 *
 * Raw coordinate numbers only mean something for a fixed model, layer,
 * tokenizer, and basis.  First test a stable relation/direction or subspace.
 * If it exists, an explicit basis transform can make that relation easier to
 * inspect.
 */

int main(void)
{
  size_t i;
  static const uint32_t lf[] = {0x000Au};
  static const uint32_t crlf[] = {0x000Du, 0x000Au};
  static const uint32_t value_pipe[] = {0x007Cu, 0x003Eu};
  static const uint32_t mario_pipe[] = {0x2566u, 0x2502u};
  static const uint32_t arrows[] = {0x2190u, 0x2192u};

  make_stdout_binary();

  printf("# glyph-bytes-v1\n");
  printf("# numeric scalar -> explicit UTF-8 bytes -> printf-visible glyph\n");

  printf("# controls\n");
  print_codepoint(0x0009u, "control", "TAB");
  print_codepoint(0x000Au, "control", "LF");
  print_codepoint(0x000Du, "control", "CR");

  printf("# line-ending sequences\n");
  print_sequence(lf, sizeof lf / sizeof lf[0], "sequence", "LF");
  print_sequence(crlf, sizeof crlf / sizeof crlf[0], "sequence", "CRLF");

  printf("# current-software-keyboard unique codepoints\n");
  for (i = 0; i < sizeof keyboard_codepoints / sizeof keyboard_codepoints[0]; ++i)
    print_codepoint(keyboard_codepoints[i], "software-keyboard", NULL);

  printf("# discussion-and-programmers-keyboard candidates\n");
  for (i = 0; i < sizeof discussion_codepoints / sizeof discussion_codepoints[0]; ++i)
    print_codepoint(discussion_codepoints[i].cp, "discussion",
                    discussion_codepoints[i].note);

  printf("# illustrative multi-codepoint sequences\n");
  print_sequence(value_pipe, sizeof value_pipe / sizeof value_pipe[0],
                 "sequence", "ASCII value-pipe token");
  print_sequence(mario_pipe, sizeof mario_pipe / sizeof mario_pipe[0],
                 "sequence", "flared-top pipe: U+2566 then U+2502");
  print_sequence(arrows, sizeof arrows / sizeof arrows[0],
                 "sequence", "left/right relation pair");

  return 0;
}
