/* Unmatched research draft. PAL main 0x00470970: 32 bytes; BYTES 11/32, five words differ. Scheduling and temporary-register allocation differ; return type is not established. No matching progress claimed. */
#include "common.h"

void func_00470970(void *object, u64 high, u64 low, u64 byte1, u64 byte2)
{ *(u64 *)((u8 *)object + 0x38) = (high << 32) | low | (byte1 << 8) | (byte2 << 16); }
