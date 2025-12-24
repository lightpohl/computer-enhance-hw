from typing import Dict, Optional

SIM_REGISTERS: Dict[str, int] = {}

HALF_REGS = ["al", "bl", "cl", "dl", "ah", "bh", "ch", "dh"]


def get_half_reg(src: str) -> int:
    full_reg = f"{src[0]}x"
    val = SIM_REGISTERS[full_reg]

    if src[-1] == "l":
        return val & 0xFF

    return val >> 8


def update_half_reg(dst: str, new_val: int):
    full_reg = f"{dst[0]}x"

    if full_reg not in SIM_REGISTERS:
        SIM_REGISTERS[full_reg] = 0

    prev = SIM_REGISTERS[full_reg]
    if dst[-1] == "l":
        SIM_REGISTERS[full_reg] = (prev & 0xFF00) | new_val
    else:
        SIM_REGISTERS[full_reg] = (prev & 0x00FF) | (new_val << 8)

    return f" ; {full_reg}:{prev:#x}->{SIM_REGISTERS[full_reg]:#x}"


def update_full_reg(dst: str, new_val: int):
    if dst not in SIM_REGISTERS:
        SIM_REGISTERS[dst] = 0

    prev = SIM_REGISTERS[dst]
    SIM_REGISTERS[dst] = new_val

    return f" ; {dst}:{prev:#x}->{SIM_REGISTERS[dst]:#x}"


def update_register(
    dst: str, src: Optional[str] = None, new_val: Optional[int] = None
) -> str:
    if src is None and new_val is None:
        raise Exception("src or new_val must be provided")

    if src:
        src_val = get_half_reg(src) if src in HALF_REGS else SIM_REGISTERS[src]
        return (
            update_half_reg(dst, src_val)
            if dst in HALF_REGS
            else update_full_reg(dst, src_val)
        )

    return (
        update_half_reg(dst, new_val)
        if dst in HALF_REGS
        else update_full_reg(dst, new_val)
    )
