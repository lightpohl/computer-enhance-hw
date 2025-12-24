from enum import Enum


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
    MOV_SEG_REG = "MOV_SEG_REG"
    MOV_REG_SEG = "MOV_REG_SEG"
