import sys
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

INSTRUCTION_TYPES = {
    "MOV": "MOV",
    "MOV_IMM": "MOV_IMM",
    "MOV_IMM_MEM_BYTE": "MOV_IMM_MEM_BYTE",
    "MOV_IMM_MEM_WORD": "MOV_IMM_MEM_WORD",
    "MOV_MEM_ACC": "MOV_MEM_ACC",
    "MOV_ACC_MEM": "MOV_ACC_MEM",
}

INSTRUCTION_TYPE_TO_OP_CODE = {
    "MOV": "100010",
    "MOV_IMM": "1011",
    "MOV_IMM_MEM_BYTE": "11000110",
    "MOV_IMM_MEM_WORD": "11000111",
    "MOV_MEM_ACC": "10100001",
    "MOV_ACC_MEM": "10100011",
}

INSTRUCTION_TYPE_TO_OP = {
    "MOV": "mov",
    "MOV_IMM": "mov",
    "MOV_IMM_MEM_BYTE": "mov",
    "MOV_IMM_MEM_WORD": "mov",
    "MOV_MEM_ACC": "mov",
    "MOV_ACC_MEM": "mov",
}


def get_operation(chunk: bytes) -> str:
    byte = chunk[0]
    binary_string = f"{byte:08b}"

    if binary_string == INSTRUCTION_TYPE_TO_OP_CODE["MOV_IMM_MEM_BYTE"]:
        return INSTRUCTION_TYPES["MOV_IMM_MEM_BYTE"]
    elif binary_string == INSTRUCTION_TYPE_TO_OP_CODE["MOV_IMM_MEM_WORD"]:
        return INSTRUCTION_TYPES["MOV_IMM_MEM_WORD"]
    elif binary_string == INSTRUCTION_TYPE_TO_OP_CODE["MOV_MEM_ACC"]:
        return INSTRUCTION_TYPES["MOV_MEM_ACC"]
    elif binary_string == INSTRUCTION_TYPE_TO_OP_CODE["MOV_ACC_MEM"]:
        return INSTRUCTION_TYPES["MOV_ACC_MEM"]
    elif binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE["MOV"]):
        return INSTRUCTION_TYPES["MOV"]
    elif binary_string.startswith(INSTRUCTION_TYPE_TO_OP_CODE["MOV_IMM"]):
        return INSTRUCTION_TYPES["MOV_IMM"]
    else:
        raise Exception(f"unsupported op_code: 0x{byte:02x} ({binary_string})")


def get_mod(byte: int) -> int:
    return (byte >> 6) & 3


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
    elif displacement < 0:
        return f"[{r_m_text} - {abs(displacement)}]"
    else:
        return f"[{r_m_text} + {displacement}]"


def get_operands(chunk: bytes, operation: str) -> str:
    if operation == INSTRUCTION_TYPES["MOV"]:
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
    elif operation == INSTRUCTION_TYPES["MOV_IMM"]:
        w_bit = (chunk[0] >> 3) & 1
        dst = get_reg_imm(w_bit, chunk[0])
        data = read_le16(chunk[1], chunk[2]) if w_bit else chunk[1]
        immediate = to_signed(data, 16 if w_bit else 8)

        return f"{dst}, {immediate}"
    elif operation == INSTRUCTION_TYPES["MOV_IMM_MEM_BYTE"]:
        mod = get_mod(chunk[1])
        r_m = chunk[1] & 0b111
        immediate = to_signed(chunk[2] if mod == 0b11 else chunk[-1], 8)

        if mod == 0b11:
            dst = get_reg(1, 0, True, chunk[1])
            return f"{dst}, byte {immediate}"
        elif mod == 0b00:
            if r_m == 0b110:
                displacement = read_le16(chunk[2], chunk[3])
                return f"[{displacement}], byte {immediate}"
            else:
                r_m_text = R_M_LOOKUP[r_m]
                return f"{format_memory_address(r_m_text, 0)}, byte {immediate}"
        elif mod == 0b01:
            r_m_text = R_M_LOOKUP[r_m]
            displacement = to_signed(chunk[2] if r_m != 0b110 else 0, 8)
            return f"{format_memory_address(r_m_text, displacement)}, byte {immediate}"
        elif mod == 0b10:
            r_m_text = R_M_LOOKUP[r_m]
            displacement = to_signed(read_le16(chunk[2], chunk[3]), 16)
            return f"{format_memory_address(r_m_text, displacement)}, byte {immediate}"
    elif operation == INSTRUCTION_TYPES["MOV_IMM_MEM_WORD"]:
        mod = get_mod(chunk[1])
        r_m = chunk[1] & 0b111
        immediate = to_signed(read_le16(chunk[-2], chunk[-1]), 16)

        if mod == 0b11:
            dst = get_reg(1, 1, True, chunk[1])
            return f"{dst}, word {immediate}"
        elif mod == 0b00:
            if r_m == 0b110:
                displacement = read_le16(chunk[2], chunk[3])
                return f"[{displacement}], word {immediate}"
            else:
                r_m_text = R_M_LOOKUP[r_m]
                return f"{format_memory_address(r_m_text, 0)}, word {immediate}"
        elif mod == 0b01:
            r_m_text = R_M_LOOKUP[r_m]
            displacement = to_signed(chunk[2], 8)
            return f"{format_memory_address(r_m_text, displacement)}, word {immediate}"
        elif mod == 0b10:
            r_m_text = R_M_LOOKUP[r_m]
            displacement = to_signed(read_le16(chunk[2], chunk[3]), 16)
            return f"{format_memory_address(r_m_text, displacement)}, word {immediate}"
    elif operation == INSTRUCTION_TYPES["MOV_MEM_ACC"]:
        displacement = read_le16(chunk[1], chunk[2])
        return f"ax, [{displacement}]"
    elif operation == INSTRUCTION_TYPES["MOV_ACC_MEM"]:
        displacement = read_le16(chunk[1], chunk[2])
        return f"[{displacement}], ax"

    raise Exception("unsupported operation")


def read_additional_chunks(
    file: BinaryIO, operation: str, base_chunk: bytes
) -> Optional[bytes]:
    additional_chunk = None
    if operation == INSTRUCTION_TYPES["MOV"]:
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
    elif operation == INSTRUCTION_TYPES["MOV_IMM"]:
        w_bit = (base_chunk[0] >> 3) & 1
        additional_chunk = file.read(2 if w_bit else 1)
    elif operation == INSTRUCTION_TYPES["MOV_IMM_MEM_BYTE"]:
        additional_chunk = file.read(1)
        mod = get_mod(additional_chunk[0])
        if mod == 0b11:
            additional_chunk += file.read(1)
        elif mod == 0b00:
            r_m = additional_chunk[0] & 0b111
            if r_m == 0b110:
                additional_chunk += file.read(2)
            additional_chunk += file.read(1)
        elif mod == 0b01:
            additional_chunk += file.read(2)
        elif mod == 0b10:
            additional_chunk += file.read(3)
    elif operation == INSTRUCTION_TYPES["MOV_IMM_MEM_WORD"]:
        additional_chunk = file.read(1)
        mod = get_mod(additional_chunk[0])
        if mod == 0b11:
            additional_chunk += file.read(2)
        elif mod == 0b00:
            r_m = additional_chunk[0] & 0b111
            if r_m == 0b110:
                additional_chunk += file.read(2)
            additional_chunk += file.read(2)
        elif mod == 0b01:
            additional_chunk += file.read(3)
        elif mod == 0b10:
            additional_chunk += file.read(4)
    elif operation == INSTRUCTION_TYPES["MOV_MEM_ACC"]:
        additional_chunk = file.read(2)
    elif operation == INSTRUCTION_TYPES["MOV_ACC_MEM"]:
        additional_chunk = file.read(2)

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

            operation = get_operation(chunk)
            additional_chunk = read_additional_chunks(file, operation, chunk)

            if additional_chunk:
                chunk += additional_chunk

            operands = get_operands(chunk, operation)
            print(f"{INSTRUCTION_TYPE_TO_OP[operation]} {operands}")


if __name__ == "__main__":
    main()
