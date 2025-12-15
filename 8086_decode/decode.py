import sys
from enum import Enum
from typing import BinaryIO, Optional

REG_LOOKUP = {
    0b0000: "al",
    0b0001: "ax",
    0b0010: "cl",
    0b0011: "cx",
    0b0100: "dl",
    0b0101: "dx",
    0b0110: "bl",
    0b0111: "bx",
    0b1000: "ah",
    0b1001: "sp",
    0b1010: "ch",
    0b1011: "bp",
    0b1100: "dh",
    0b1101: "si",
    0b1110: "bh",
    0b1111: "di",
}

R_M_LOOKUP = {
    0b000: "bx + si",
    0b001: "bx + di",
    0b010: "bp + si",
    0b011: "bp + di",
    0b100: "si",
    0b101: "di",
    0b110: "bp",
    0b111: "bx",
}


class InstructionType(str, Enum):
    MOV = "MOV"
    MOV_IMM = "MOV_IMM"
    MOV_IMM_MEM = "MOV_IMM_MEM"
    MOV_MEM_ACC = "MOV_MEM_ACC"
    MOV_ACC_MEM = "MOV_ACC_MEM"
    ADD = "ADD"
    ADD_IMM_MEM = "ADD_IMM_MEM"
    ADD_IMM_ACC = "ADD_IMM_ACC"
    SUB = "SUB"
    SUB_IMM_MEM = "SUB_IMM_MEM"
    SUB_IMM_ACC = "SUB_IMM_ACC"
    CMP = "CMP"
    CMP_IMM_MEM = "CMP_IMM_MEM"
    CMP_IMM_ACC = "CMP_IMM_ACC"
    JMP_JE = "JMP_JE"
    JMP_JL = "JMP_JL"
    JMP_JLE = "JMP_JLE"
    JMP_JB = "JMP_JB"
    JMP_JBE = "JMP_JBE"
    JMP_JP = "JMP_JP"
    JMP_JO = "JMP_JO"
    JMP_JS = "JMP_JS"
    JMP_JNE = "JMP_JNE"
    JMP_JNL = "JMP_JNL"
    JMP_JNLE = "JMP_JNLE"
    JMP_JNB = "JMP_JNB"
    JMP_JNBE = "JMP_JNBE"
    JMP_JNP = "JMP_JNP"
    JMP_JNO = "JMP_JNO"
    JMP_JNS = "JMP_JNS"
    LOOP = "LOOP"
    LOOPZ = "LOOPZ"
    LOOPNZ = "LOOPNZ"
    JCXZ = "JCXZ"


class LengthClass(str, Enum):
    REG_MEM = "REG_MEM"
    IMM_REG = "IMM_REG"
    IMM_MEM = "IMM_MEM"
    MEM_ACC = "MEM_ACC"
    ACC_MEM = "ACC_MEM"
    ACC_IMM = "ACC_IMM"
    JMP_SHORT = "JMP_SHORT"


IMM_TO_RM_OPCODE = "100000"
INSTRUCTION_TYPE_TO_OP_CODE = {
    InstructionType.MOV: "100010",
    InstructionType.MOV_IMM: "1011",
    InstructionType.MOV_IMM_MEM: "1100011",
    InstructionType.MOV_MEM_ACC: "10100001",
    InstructionType.MOV_ACC_MEM: "10100011",
    InstructionType.ADD: "000000",
    InstructionType.ADD_IMM_MEM: IMM_TO_RM_OPCODE,
    InstructionType.ADD_IMM_ACC: "0000010",
    InstructionType.SUB: "001010",
    InstructionType.SUB_IMM_MEM: IMM_TO_RM_OPCODE,
    InstructionType.SUB_IMM_ACC: "0010110",
    InstructionType.CMP: "001110",
    InstructionType.CMP_IMM_MEM: IMM_TO_RM_OPCODE,
    InstructionType.CMP_IMM_ACC: "0011110",
    InstructionType.JMP_JE: "01110100",
    InstructionType.JMP_JL: "01111100",
    InstructionType.JMP_JLE: "01111110",
    InstructionType.JMP_JB: "01110010",
    InstructionType.JMP_JBE: "01110110",
    InstructionType.JMP_JP: "01111010",
    InstructionType.JMP_JO: "01110000",
    InstructionType.JMP_JS: "01111000",
    InstructionType.JMP_JNE: "01110101",
    InstructionType.JMP_JNL: "01111101",
    InstructionType.JMP_JNLE: "01111111",
    InstructionType.JMP_JNB: "01110011",
    InstructionType.JMP_JNBE: "01110111",
    InstructionType.JMP_JNP: "01111011",
    InstructionType.JMP_JNO: "01110001",
    InstructionType.JMP_JNS: "01111001",
    InstructionType.LOOPNZ: "11100000",
    InstructionType.LOOPZ: "11100001",
    InstructionType.LOOP: "11100010",
    InstructionType.JCXZ: "11100011",
}

INSTRUCTION_TYPE_TO_OP = {
    InstructionType.MOV: "mov",
    InstructionType.MOV_IMM: "mov",
    InstructionType.MOV_IMM_MEM: "mov",
    InstructionType.MOV_MEM_ACC: "mov",
    InstructionType.MOV_ACC_MEM: "mov",
    InstructionType.ADD: "add",
    InstructionType.ADD_IMM_MEM: "add",
    InstructionType.ADD_IMM_ACC: "add",
    InstructionType.SUB: "sub",
    InstructionType.SUB_IMM_MEM: "sub",
    InstructionType.SUB_IMM_ACC: "sub",
    InstructionType.CMP: "cmp",
    InstructionType.CMP_IMM_MEM: "cmp",
    InstructionType.CMP_IMM_ACC: "cmp",
    InstructionType.JMP_JE: "je",
    InstructionType.JMP_JL: "jl",
    InstructionType.JMP_JLE: "jle",
    InstructionType.JMP_JB: "jb",
    InstructionType.JMP_JBE: "jbe",
    InstructionType.JMP_JP: "jp",
    InstructionType.JMP_JO: "jo",
    InstructionType.JMP_JS: "js",
    InstructionType.JMP_JNE: "jne",
    InstructionType.JMP_JNL: "jnl",
    InstructionType.JMP_JNLE: "jnle",
    InstructionType.JMP_JNB: "jnb",
    InstructionType.JMP_JNBE: "jnbe",
    InstructionType.JMP_JNP: "jnp",
    InstructionType.JMP_JNO: "jno",
    InstructionType.JMP_JNS: "jns",
    InstructionType.LOOP: "loop",
    InstructionType.LOOPZ: "loopz",
    InstructionType.LOOPNZ: "loopnz",
    InstructionType.JCXZ: "jcxz",
}


def get_length_class(byte: int) -> LengthClass:
    binary_string = f"{byte:08b}"

    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV]):
        return LengthClass.REG_MEM
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.ADD]):
        return LengthClass.REG_MEM
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.SUB]):
        return LengthClass.REG_MEM
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.CMP]):
        return LengthClass.REG_MEM
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_IMM]):
        return LengthClass.IMM_REG
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.ADD_IMM_ACC]
    ):
        return LengthClass.ACC_IMM
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.SUB_IMM_ACC]
    ):
        return LengthClass.ACC_IMM
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.CMP_IMM_ACC]
    ):
        return LengthClass.ACC_IMM
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_IMM_MEM]
    ):
        return LengthClass.IMM_MEM
    if binary_string.startswith(IMM_TO_RM_OPCODE):
        return LengthClass.IMM_MEM
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_MEM_ACC]
    ):
        return LengthClass.MEM_ACC
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_ACC_MEM]
    ):
        return LengthClass.ACC_MEM
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JE]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JL]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JLE]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JB]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JBE]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JP]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JO]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JS]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNE]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNL]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNLE]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNB]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNBE]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNP]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNO]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNS]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.LOOP]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.LOOPZ]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.LOOPNZ]):
        return LengthClass.JMP_SHORT
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JCXZ]):
        return LengthClass.JMP_SHORT

    raise Exception(f"unsupported op_code for length: {binary_string}")


def get_operation(chunk: bytes) -> InstructionType:
    byte0 = chunk[0]
    binary_string = f"{byte0:08b}"

    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_IMM_MEM]
    ):
        return InstructionType.MOV_IMM_MEM
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_MEM_ACC]
    ):
        return InstructionType.MOV_MEM_ACC
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_ACC_MEM]
    ):
        return InstructionType.MOV_ACC_MEM
    if binary_string.startswith(IMM_TO_RM_OPCODE):
        local_op_code = get_local_op_code(chunk[1])
        if local_op_code == 0b000:
            return InstructionType.ADD_IMM_MEM
        elif local_op_code == 0b101:
            return InstructionType.SUB_IMM_MEM
        elif local_op_code == 0b111:
            return InstructionType.CMP_IMM_MEM
        else:
            raise Exception(f"unsupported local op_code: {local_op_code}")
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.ADD_IMM_ACC]
    ):
        return InstructionType.ADD_IMM_ACC
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.SUB_IMM_ACC]
    ):
        return InstructionType.SUB_IMM_ACC
    if binary_string.startswith(
        INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.CMP_IMM_ACC]
    ):
        return InstructionType.CMP_IMM_ACC
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.ADD]):
        return InstructionType.ADD
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.SUB]):
        return InstructionType.SUB
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.CMP]):
        return InstructionType.CMP
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV_IMM]):
        return InstructionType.MOV_IMM
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.MOV]):
        return InstructionType.MOV
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JE]):
        return InstructionType.JMP_JE
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JL]):
        return InstructionType.JMP_JL
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JLE]):
        return InstructionType.JMP_JLE
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JB]):
        return InstructionType.JMP_JB
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JBE]):
        return InstructionType.JMP_JBE
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JP]):
        return InstructionType.JMP_JP
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JO]):
        return InstructionType.JMP_JO
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JS]):
        return InstructionType.JMP_JS
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNE]):
        return InstructionType.JMP_JNE
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNL]):
        return InstructionType.JMP_JNL
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNLE]):
        return InstructionType.JMP_JNLE
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNB]):
        return InstructionType.JMP_JNB
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNBE]):
        return InstructionType.JMP_JNBE
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNP]):
        return InstructionType.JMP_JNP
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNO]):
        return InstructionType.JMP_JNO
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JMP_JNS]):
        return InstructionType.JMP_JNS
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.LOOP]):
        return InstructionType.LOOP
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.LOOPZ]):
        return InstructionType.LOOPZ
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.LOOPNZ]):
        return InstructionType.LOOPNZ
    if binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE[InstructionType.JCXZ]):
        return InstructionType.JCXZ

    raise Exception(f"unsupported op_code: {binary_string}")


def get_mod(byte: int) -> int:
    return (byte >> 6) & 3


def get_local_op_code(byte: int) -> int:
    return (byte >> 3) & 0b111


def get_reg(d_bit: int, w_bit: int, destination: bool, byte: int) -> str:
    target_bit_start = 3 if (destination == bool(d_bit)) else 0

    reg_bits = (byte >> target_bit_start) & 0b111
    key = (reg_bits << 1) | w_bit

    return REG_LOOKUP[key]


def get_reg_imm(w_bit: int, byte: int) -> int:
    reg_bits = byte & 0b111
    key = (reg_bits << 1) | w_bit

    return REG_LOOKUP[key]


def read_le16(low_byte: int, high_byte: int) -> int:
    return low_byte | (high_byte << 8)


def to_signed(value: int, bits: int) -> int:
    if bits == 8:
        if value >= 128:
            return value - 256
    elif bits == 16:
        if value >= 32768:
            return value - 65536
    return value


def format_memory_address(r_m_text: str, displacement: int) -> str:
    if displacement == 0:
        return f"[{r_m_text}]"

    if displacement < 0:
        return f"[{r_m_text} - {abs(displacement)}]"

    return f"[{r_m_text} + {displacement}]"


def format_imm_mem_operands(chunk: bytes, w_bit: int, immediate: int) -> str:
    size_text = "word" if w_bit else "byte"
    mod = get_mod(chunk[1])
    r_m = chunk[1] & 0b111

    if mod == 0b11:
        dst = get_reg(1, w_bit, True, chunk[1])
        return f"{dst}, {size_text} {immediate}"
    elif mod == 0b00:
        if r_m == 0b110:
            displacement = read_le16(chunk[2], chunk[3])
            return f"[{displacement}], {size_text} {immediate}"
        else:
            r_m_text = R_M_LOOKUP[r_m]
            return f"{format_memory_address(r_m_text, 0)}, {size_text} {immediate}"
    elif mod == 0b01:
        r_m_text = R_M_LOOKUP[r_m]
        displacement = to_signed(chunk[2] if r_m != 0b110 else 0, 8)
        return (
            f"{format_memory_address(r_m_text, displacement)}, {size_text} {immediate}"
        )
    elif mod == 0b10:
        r_m_text = R_M_LOOKUP[r_m]
        displacement = to_signed(read_le16(chunk[2], chunk[3]), 16)
        return (
            f"{format_memory_address(r_m_text, displacement)}, {size_text} {immediate}"
        )


def get_operands(chunk: bytes, operation: InstructionType) -> str:
    if (
        operation == InstructionType.MOV
        or operation == InstructionType.ADD
        or operation == InstructionType.SUB
        or operation == InstructionType.CMP
    ):
        mod = get_mod(chunk[1])
        d_bit = (chunk[0] >> 1) & 1
        w_bit = chunk[0] & 1

        if mod == 0b11:
            dst = get_reg(d_bit, w_bit, True, chunk[1])
            src = get_reg(d_bit, w_bit, False, chunk[1])
            return f"{dst}, {src}"
        elif mod == 0b00:
            r_m = chunk[1] & 0b111
            if r_m == 0b110:
                displacement = read_le16(chunk[2], chunk[3])
                mem_addr = format_memory_address(str(displacement), 0)
            else:
                r_m_text = R_M_LOOKUP[r_m]
                mem_addr = format_memory_address(r_m_text, 0)

            if d_bit:
                dst = get_reg(d_bit, w_bit, True, chunk[1])
                return f"{dst}, {mem_addr}"
            else:
                src = get_reg(d_bit, w_bit, False, chunk[1])
                return f"{mem_addr}, {src}"
        elif mod == 0b01:
            r_m = chunk[1] & 0b111
            r_m_text = R_M_LOOKUP[r_m]
            displacement = to_signed(chunk[2], 8)
            mem_addr = format_memory_address(r_m_text, displacement)

            if d_bit:
                dst = get_reg(d_bit, w_bit, True, chunk[1])
                return f"{dst}, {mem_addr}"
            else:
                src = get_reg(d_bit, w_bit, False, chunk[1])
                return f"{mem_addr}, {src}"
        elif mod == 0b10:
            r_m = chunk[1] & 0b111
            r_m_text = R_M_LOOKUP[r_m]
            displacement = to_signed(read_le16(chunk[2], chunk[3]), 16)
            mem_addr = format_memory_address(r_m_text, displacement)

            if d_bit:
                dst = get_reg(d_bit, w_bit, True, chunk[1])
                return f"{dst}, {mem_addr}"
            else:
                src = get_reg(d_bit, w_bit, False, chunk[1])
                return f"{mem_addr}, {src}"

    if operation == InstructionType.MOV_IMM:
        w_bit = (chunk[0] >> 3) & 1
        dst = get_reg_imm(w_bit, chunk[0])
        data = read_le16(chunk[1], chunk[2]) if w_bit else chunk[1]
        immediate = to_signed(data, 16 if w_bit else 8)

        return f"{dst}, {immediate}"

    if operation in (
        InstructionType.ADD_IMM_ACC,
        InstructionType.SUB_IMM_ACC,
        InstructionType.CMP_IMM_ACC,
    ):
        w_bit = chunk[0] & 1
        dst = "ax" if w_bit else "al"
        data = read_le16(chunk[1], chunk[2]) if w_bit else chunk[1]
        immediate = to_signed(data, 16 if w_bit else 8)

        return f"{dst}, {immediate}"

    if operation == InstructionType.MOV_IMM_MEM:
        w_bit = chunk[0] & 1
        if w_bit:
            immediate_raw = read_le16(chunk[-2], chunk[-1])
            immediate = to_signed(immediate_raw, 16)
        else:
            immediate = to_signed(chunk[-1], 8)
        return format_imm_mem_operands(chunk, w_bit, immediate)

    if operation in (
        InstructionType.ADD_IMM_MEM,
        InstructionType.SUB_IMM_MEM,
        InstructionType.CMP_IMM_MEM,
    ):
        op_byte = chunk[0]
        w_bit = op_byte & 1
        s_bit = (op_byte >> 1) & 1
        if w_bit and not s_bit:
            immediate_raw = read_le16(chunk[-2], chunk[-1])
            immediate = to_signed(immediate_raw, 16)
        else:
            immediate = to_signed(chunk[-1], 8)
        return format_imm_mem_operands(chunk, w_bit, immediate)

    if operation == InstructionType.MOV_MEM_ACC:
        displacement = read_le16(chunk[1], chunk[2])
        return f"ax, [{displacement}]"

    if operation == InstructionType.MOV_ACC_MEM:
        displacement = read_le16(chunk[1], chunk[2])
        return f"[{displacement}], ax"

    if operation in (
        InstructionType.JMP_JE,
        InstructionType.JMP_JL,
        InstructionType.JMP_JLE,
        InstructionType.JMP_JB,
        InstructionType.JMP_JBE,
        InstructionType.JMP_JP,
        InstructionType.JMP_JO,
        InstructionType.JMP_JS,
        InstructionType.JMP_JNE,
        InstructionType.JMP_JNL,
        InstructionType.JMP_JNLE,
        InstructionType.JMP_JNB,
        InstructionType.JMP_JNBE,
        InstructionType.JMP_JNP,
        InstructionType.JMP_JNO,
        InstructionType.JMP_JNS,
        InstructionType.LOOP,
        InstructionType.LOOPZ,
        InstructionType.LOOPNZ,
        InstructionType.JCXZ,
    ):
        offset = to_signed(chunk[1], 8)
        return f"{offset}"

    raise Exception(f"unsupported operation: {operation}")


def read_additional_chunks(
    file: BinaryIO, length_class: LengthClass, base_chunk: bytes
) -> Optional[bytes]:
    additional_chunk = None
    if length_class == LengthClass.REG_MEM:
        additional_chunk = file.read(1)
        mod = get_mod(additional_chunk[0])
        if mod == 0b00:
            r_m = additional_chunk[0] & 0b111
            if r_m == 0b110:
                additional_chunk += file.read(2)
        elif mod == 0b01:
            additional_chunk += file.read(1)
        elif mod == 0b10:
            additional_chunk += file.read(2)
    elif length_class == LengthClass.IMM_REG:
        w_bit = (base_chunk[0] >> 3) & 1
        additional_chunk = file.read(2 if w_bit else 1)
    elif length_class == LengthClass.ACC_IMM:
        w_bit = base_chunk[0] & 1
        additional_chunk = file.read(2 if w_bit else 1)
    elif length_class == LengthClass.IMM_MEM:
        w_bit = base_chunk[0] & 1
        binary_string = f"{base_chunk[0]:08b}"

        if binary_string.startswith(IMM_TO_RM_OPCODE):
            s_bit = (base_chunk[0] >> 1) & 1
            immediate_size = 1 if (w_bit and s_bit) or not w_bit else 2
        else:
            immediate_size = 2 if w_bit else 1

        additional_chunk = file.read(1)
        mod = get_mod(additional_chunk[0])
        if mod == 0b11:
            additional_chunk += file.read(immediate_size)
        elif mod == 0b00:
            r_m = additional_chunk[0] & 0b111
            if r_m == 0b110:
                additional_chunk += file.read(2)
            additional_chunk += file.read(immediate_size)
        elif mod == 0b01:
            additional_chunk += file.read(1 + immediate_size)
        elif mod == 0b10:
            additional_chunk += file.read(2 + immediate_size)
    elif length_class == LengthClass.MEM_ACC:
        additional_chunk = file.read(2)
    elif length_class == LengthClass.ACC_MEM:
        additional_chunk = file.read(2)
    elif length_class == LengthClass.JMP_SHORT:
        additional_chunk = file.read(1)

    return additional_chunk


def main():
    file_path = sys.argv[1]

    if not file_path:
        print("no file_path provided")
        sys.exit(1)

    with open(file_path, "rb") as file:
        print(f"; {file.name}:")
        print("bits 16")

        while True:
            chunk = file.read(1)

            if not chunk:
                break

            length_class = get_length_class(chunk[0])
            additional_chunk = read_additional_chunks(file, length_class, chunk)

            if additional_chunk:
                chunk += additional_chunk

            operation = get_operation(chunk)
            operands = get_operands(chunk, operation)
            print(f"{INSTRUCTION_TYPE_TO_OP[operation]} {operands}")


if __name__ == "__main__":
    main()
