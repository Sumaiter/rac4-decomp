/* Unmatched research draft. PAL main 0x004ABFC0: 36 bytes; BYTES 4/36, one word differs (shift versus signed comparison). No matching progress claimed. */
#include "common.h"

typedef struct { u8 pad00[0x16C]; s32 flags; } Record;
extern Record D_00308C80[];
s32 func_004ABFC0(s32 index) { return (~D_00308C80[index].flags) < 0; }
