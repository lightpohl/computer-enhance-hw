from typing import Dict, Optional

from utils import InstructionType

SIM_REGISTERS: Dict[str, int] = {}
SIM_FLAGS: Dict[str, bool] = {"Z": False, "S": False}

HALF_REGS = ["al", "bl", "cl", "dl", "ah", "bh", "ch", "dh"]


def get_half_reg(src: str) -> int:
    full_reg = f"{src[0]}x"

    if full_reg not in SIM_REGISTERS:
        SIM_REGISTERS[full_reg] = 0

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
        SIM_REGISTERS[full_reg] = (prev & 0xFF00) | (new_val & 0xFF)
    else:
        SIM_REGISTERS[full_reg] = (prev & 0x00FF) | ((new_val & 0xFF) << 8)

    return f" ; {full_reg}:0x{prev:04x}->0x{SIM_REGISTERS[full_reg]:04x}"


def get_full_reg(dst: str):
    if dst not in SIM_REGISTERS:
        SIM_REGISTERS[dst] = 0

    return SIM_REGISTERS[dst]


def update_full_reg(dst: str, new_val: int):
    if dst not in SIM_REGISTERS:
        SIM_REGISTERS[dst] = 0

    prev = SIM_REGISTERS[dst]
    SIM_REGISTERS[dst] = new_val & 0xFFFF

    return f" ; {dst}:0x{prev:04x}->0x{SIM_REGISTERS[dst]:04x}"


def format_flags() -> str:
    result = ""
    for key in SIM_FLAGS:
        if SIM_FLAGS[key]:
            result += key

    return result


def update_flags(result: int, is_wide: bool) -> str:
    before_flags = format_flags()

    if is_wide:
        masked_result = result & 0xFFFF
        SIM_FLAGS["S"] = (masked_result & 0x8000) != 0
        SIM_FLAGS["Z"] = masked_result == 0
    else:
        masked_result = result & 0xFF
        SIM_FLAGS["S"] = (masked_result & 0x80) != 0
        SIM_FLAGS["Z"] = masked_result == 0

    after_flags = format_flags()

    if before_flags != after_flags:
        return f" flags:{before_flags}->{after_flags}"

    return ""


def update_simulation(
    dst: str,
    operation: InstructionType,
    src: Optional[str] = None,
    immediate: Optional[int] = None,
) -> str:
    if src is None and immediate is None:
        raise Exception("src or immediate must be provided")

    dst_val = get_half_reg(dst) if dst in HALF_REGS else get_full_reg(dst)

    is_mov = operation in (
        InstructionType.MOV,
        InstructionType.MOV_IMM,
        InstructionType.MOV_IMM_MEM,
        InstructionType.MOV_SEG_REG,
        InstructionType.MOV_REG_SEG,
    )

    is_cmp = operation in (
        InstructionType.CMP,
        InstructionType.CMP_IMM_ACC,
        InstructionType.CMP_IMM_MEM,
    )

    is_add = operation in (
        InstructionType.ADD,
        InstructionType.ADD_IMM_ACC,
        InstructionType.ADD_IMM_MEM,
    )

    is_sub = operation in (
        InstructionType.SUB,
        InstructionType.SUB_IMM_ACC,
        InstructionType.SUB_IMM_MEM,
    )

    if src:
        src_val = get_half_reg(src) if src in HALF_REGS else get_full_reg(src)
        new_val = src_val

        if is_mov:
            return (
                update_half_reg(dst, new_val)
                if dst in HALF_REGS
                else update_full_reg(dst, new_val)
            )

        if is_cmp:
            new_val = dst_val - src_val
            return f" ;{update_flags(new_val, dst not in HALF_REGS)}"

        if is_add:
            new_val = dst_val + src_val

        if is_sub:
            new_val = dst_val - src_val

        return (
            (
                update_half_reg(dst, new_val)
                if dst in HALF_REGS
                else update_full_reg(dst, new_val)
            )
            + update_flags(new_val, dst not in HALF_REGS)
            if is_add or is_sub
            else ""
        )

    new_val = immediate
    if is_mov:
        return (
            update_half_reg(dst, new_val)
            if dst in HALF_REGS
            else update_full_reg(dst, new_val)
        )

    if is_cmp:
        new_val = dst_val - new_val
        return f" ;{update_flags(new_val, dst not in HALF_REGS)}"

    if is_add:
        new_val = dst_val + immediate
        return (
            update_half_reg(dst, new_val)
            if dst in HALF_REGS
            else update_full_reg(dst, new_val)
        ) + update_flags(new_val, dst not in HALF_REGS)

    if is_sub:
        new_val = dst_val - immediate
        return (
            update_half_reg(dst, new_val)
            if dst in HALF_REGS
            else update_full_reg(dst, new_val)
        ) + update_flags(new_val, dst not in HALF_REGS)

    return ""
