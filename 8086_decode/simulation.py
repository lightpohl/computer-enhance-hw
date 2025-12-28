from typing import Dict, Optional

from utils import InstructionType

HALF_REGS = ["al", "bl", "cl", "dl", "ah", "bh", "ch", "dh"]
PREV_SIM_REGISTERS: Dict[str, int] = {"ip": 0}
SIM_REGISTERS: Dict[str, int] = {
    "ip": 0,
}
SIM_FLAGS: Dict[str, bool] = {"Z": False, "S": False}
SIM_MEMORY: list[int] = [0] * (1024 * 1024)


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

    if full_reg not in PREV_SIM_REGISTERS:
        PREV_SIM_REGISTERS[full_reg] = 0

    prev = SIM_REGISTERS[full_reg]
    PREV_SIM_REGISTERS[full_reg] = prev

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

    if dst not in PREV_SIM_REGISTERS:
        PREV_SIM_REGISTERS[dst] = 0

    prev = SIM_REGISTERS[dst]
    PREV_SIM_REGISTERS[dst] = prev
    SIM_REGISTERS[dst] = new_val & 0xFFFF

    return f" ; {dst}:0x{prev:04x}->0x{SIM_REGISTERS[dst]:04x}"


def get_ip_register() -> tuple[int, int]:
    return (SIM_REGISTERS["ip"], PREV_SIM_REGISTERS["ip"])


def set_ip_register(new_val: int) -> tuple[int, int]:
    PREV_SIM_REGISTERS["ip"] = SIM_REGISTERS["ip"]
    SIM_REGISTERS["ip"] = new_val
    return (SIM_REGISTERS["ip"], PREV_SIM_REGISTERS["ip"])


def get_memory(loc: int) -> int:
    low = SIM_MEMORY[loc]
    high = SIM_MEMORY[loc + 1]
    return (high << 8) | low


def set_memory(loc: int, new_val: int):
    SIM_MEMORY[loc] = new_val & 0xFF
    SIM_MEMORY[loc + 1] = (new_val >> 8) & 0xFF


def load_code(code: bytes):
    for i, byte in enumerate(code):
        SIM_MEMORY[i] = byte


def get_code_byte(address: int) -> int:
    if address >= len(SIM_MEMORY):
        raise Exception(f"Address {address} exceeds memory size")
    return SIM_MEMORY[address]


def grab_chunk_from_memory(working_ip: int, amount: int) -> tuple[bytes, int]:
    chunk = bytes(get_code_byte(working_ip + i) for i in range(amount))
    return chunk, working_ip + amount


R_M_BASE_REGS = {
    0b000: ("bx", "si"),
    0b001: ("bx", "di"),
    0b010: ("bp", "si"),
    0b011: ("bp", "di"),
    0b100: ("si", None),
    0b101: ("di", None),
    0b110: ("bp", None),
    0b111: ("bx", None),
}


def calc_effective_address(r_m: int, displacement: int) -> int:
    base_reg, index_reg = R_M_BASE_REGS[r_m]
    addr = get_full_reg(base_reg) + displacement
    if index_reg:
        addr += get_full_reg(index_reg)
    return addr & 0xFFFF


def format_ip() -> str:
    current_ip, prev_ip = get_ip_register()
    return f" ip:{prev_ip:#04x}->{current_ip:#04x}"


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
    src_addr: Optional[int] = None,
    dst_addr: Optional[int] = None,
) -> str:
    if src is None and immediate is None:
        raise Exception("src or immediate must be provided")

    is_mem_src = src_addr is not None
    is_mem_dst = dst_addr is not None

    if is_mem_dst:
        dst_val = get_memory(dst_addr)
    else:
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
        if is_mem_src:
            src_val = get_memory(src_addr)
        else:
            src_val = get_half_reg(src) if src in HALF_REGS else get_full_reg(src)

        if is_mov:
            new_val = src_val

            if is_mem_dst:
                set_memory(dst_addr, new_val)
                return " ;" + format_ip()
            else:
                return (
                    update_half_reg(dst, new_val)
                    if dst in HALF_REGS
                    else update_full_reg(dst, new_val)
                ) + format_ip()

        if is_cmp:
            new_val = dst_val - src_val
            return f" ;{format_ip()}{update_flags(new_val, is_mem_dst or dst not in HALF_REGS)}"

        if is_add:
            new_val = dst_val + src_val

            if is_mem_dst:
                set_memory(dst_addr, new_val)
                return " ;" + format_ip() + update_flags(new_val, True)
            else:
                return (
                    (
                        update_half_reg(dst, new_val)
                        if dst in HALF_REGS
                        else update_full_reg(dst, new_val)
                    )
                    + format_ip()
                    + update_flags(new_val, dst not in HALF_REGS)
                )

        if is_sub:
            new_val = dst_val - src_val
            if is_mem_dst:
                set_memory(dst_addr, new_val)
                return " ;" + format_ip() + update_flags(new_val, True)
            else:
                return (
                    (
                        update_half_reg(dst, new_val)
                        if dst in HALF_REGS
                        else update_full_reg(dst, new_val)
                    )
                    + format_ip()
                    + update_flags(new_val, dst not in HALF_REGS)
                )

        return ""

    if immediate is not None:
        if is_mov:
            new_val = immediate
            if is_mem_dst:
                set_memory(dst_addr, new_val)
                return " ;" + format_ip()
            else:
                return (
                    update_half_reg(dst, new_val)
                    if dst in HALF_REGS
                    else update_full_reg(dst, new_val)
                ) + format_ip()

        if is_cmp:
            new_val = dst_val - immediate
            return f" ;{format_ip()}{update_flags(new_val, is_mem_dst or dst not in HALF_REGS)}"

        if is_add:
            new_val = dst_val + immediate
            if is_mem_dst:
                set_memory(dst_addr, new_val)
                return " ;" + format_ip() + update_flags(new_val, True)
            else:
                return (
                    (
                        update_half_reg(dst, new_val)
                        if dst in HALF_REGS
                        else update_full_reg(dst, new_val)
                    )
                    + format_ip()
                    + update_flags(new_val, dst not in HALF_REGS)
                )

        if is_sub:
            new_val = dst_val - immediate
            if is_mem_dst:
                set_memory(dst_addr, new_val)
                return " ;" + format_ip() + update_flags(new_val, True)
            else:
                return (
                    (
                        update_half_reg(dst, new_val)
                        if dst in HALF_REGS
                        else update_full_reg(dst, new_val)
                    )
                    + format_ip()
                    + update_flags(new_val, dst not in HALF_REGS)
                )

    return ""
