from enum import Enum


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

SEG_REG_LOOKUP = {
    0b000: "es",
    0b001: "cs",
    0b010: "ss",
    0b011: "ds",
}

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
    InstructionType.MOV_SEG_REG: "10001110",
    InstructionType.MOV_REG_SEG: "10001100",
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
    InstructionType.MOV_SEG_REG: "mov",
    InstructionType.MOV_REG_SEG: "mov",
}
