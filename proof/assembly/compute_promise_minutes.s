.section __TEXT,__text,regular,pure_instructions
.globl _compute_promise_minutes_asm
.p2align 2
_compute_promise_minutes_asm:
    fadd d0, d0, d1
    fadd d0, d0, d2
    ret
