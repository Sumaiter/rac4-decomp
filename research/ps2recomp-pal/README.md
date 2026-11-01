# PS2Recomp-assisted PAL reconstruction

These are game reconstruction results for OpenRAC, using the local
PS2Recomp translation as a reference alongside the retail executable.
The machine-state C++ emitted by PS2Recomp is not matching C and is not
included here. All functions in `src/` below were separately reconstructed
as plain C and compiled through the unchanged OpenRAC toolchain.

Reference: SCES_532.85, OpenRAC base
`fe6ec0d2e9d209ad3a84dd33a188120ea12f030c`, PS2Recomp
`e5636981a1c9de368f6b71e819c3dc188dfedbf4`.

## New verified C

| PAL main function | Bytes | Observed behavior |
| --- | ---: | --- |
| `func_004985D0` | 28 | Read signed word at offset 4 of a record with stride 0x54, base `D_002F33B8` |
| `func_00499AE8` | 24 | Read indexed signed word from offset 0x84 of `D_002F3508` |
| `func_0049BE58` | 28 | Read signed word at offset 4 of a record with stride 0x3C, base `D_00306EC0` |
| `func_00504BF0` | 20 | Store three words, combining the middle word with bitwise OR |
| `func_0050FF90` | 28 | Follow the pointer at object offset 0x40 and write a float scaled by 5/6 at offset 0x48 |

Total: **5 canonical functions / 128 bytes**. Names describe only observed
layout and operations; no higher-level game meaning has been established.
The zero-length array in `00499AE8.c` represents an externally stored
variable-length tail using the original compiler's GNU C extension.

Every final source was compiled with `tools/cc.sh`. Each function's size
and all non-relocated instruction bits match its direct PAL catalogue
address. All six HI16/LO16 relocations in the three table lookups were
independently resolved to the addresses encoded in the PAL retail code.
The other two functions have no relocations and match all bytes directly.
`matching-evidence.json` records source hashes and relocation locations.
No compiler, assembler fixup, or matching rule was changed.

These are main-image checks. The frontend pair is listed in the index
as a relationship, not as another independently compiled/verified match.
No complete US audit was run because the US retail input is unavailable.
The existing full source build and PAL map audit predate this batch; the
five new sources were compiled and checked separately.
After adding this batch, a read-only check of the current PAL map found
6,751 matching mapped places, zero byte mismatches, and zero unavailable
source objects. This is the masked-byte map check, not a global relocation
audit; relocation targets were independently checked for the five additions.

## Unmatched reconstruction drafts

`drafts/` retains three readable C attempts for follow-up work. They are
not built as game source, not included in matching maps, and not counted
as progress. Their comments record the direct PAL comparison result:

| Draft | Retail size | Remaining byte differences |
| --- | ---: | --- |
| `func_00501B58` | 112 | 13 bytes in five setup words |
| `func_004ABFC0` | 36 | 4 bytes in one comparison word |
| `func_00470970` | 32 | 11 bytes in five words |

The hash lookup draft continues a prior attempt, with the translated
output used to review its behavior. These are provisional reconstructions;
their signatures, types and complete semantics still need review.

## Complete translation index

`translation-index.tsv` lists all **13,713 inventory ranges** translated
for the main image and frontend, including fragments. It records the
baseline OpenRAC status and whether the generated function contains
throwing placeholders. `summary.json` aggregates these rows.

- `already_matched`: catalogue name already mapped as a match.
- `new_matching_c`: one of the five new main-image matches above.
- `generated_unverified`: generated C++ exists; matching C is not established.
- `generated_with_unhandled`: generated C++ contains throwing placeholders.
- `fragment_unverified`: an inventory remnant, not a completed function.
- `paired_main_existing_match` / `paired_main_new_match`: frontend ranges
  paired with a main-image function by OpenRAC metadata; not a separate
  verification of the frontend's relocation targets.

Both translated images report 636 unhandled-instruction diagnostics.
Some concern embedded data in executable ranges. Neither their presence
nor absence establishes reachability or semantic correctness. The index
does not count generated C++ as decompilation progress.

The 47 level programs were not translated in this experiment. All 49
extracted program hashes match OpenRAC metadata, and the analyzer processed
the 16 distinct program images, but that is input validation rather than
new reconstruction work. The main-only PC probe showed a black window;
it does not establish playable native-port progress.

Regenerate the index after producing the local main/frontend translations
from `config/pal/inventory.tsv`, with CSV names `sub_<8-digit-address>`
and no stubs, skips, or instruction patches:

```sh
python research/ps2recomp-pal/build_index.py \
  --base-ref fe6ec0d2e9d209ad3a84dd33a188120ea12f030c \
  --generated-main /path/to/local/generated \
  --generated-frontbin /path/to/local/generated-frontbin
```

The index builder checks generated range headers and starting-address
registration, and uses `config/pal/frontend_pairs.tsv` to normalize shared
frontend functions. It copies no instruction words or generated game code.
No disc data, extracted binaries, disassembly, or SDK material is included.
