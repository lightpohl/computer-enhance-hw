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

INSTRUCTION_TYPE = {
    "MOV_REG_TO_REG": "100010",
    "MOV_REG_IMM": "1011",
}

INTRUCTION_TYPE_TO_TEXT = {
    "MOV_REG_TO_REG": "mov",
}


def get_operation(chunk: bytes) -> str:
    byte = chunk[0]
    binary_string = f"{byte:08b}"

    if binary_string.startswith(INSTRUCTION_TYPE["MOV_REG_TO_REG"]):
        return INTRUCTION_TYPE_TO_TEXT["MOV_REG_TO_REG"]
    elif binary_string.startswith(INSTRUCTION_TYPE["MOV_REG_IMM"]):
        return INTRUCTION_TYPE_TO_TEXT["MOV_REG_IMM"]
    else:
        raise Exception(f"unsupported op_code: 0x{byte:02x} ({binary_string})")


def get_mod(byte: int) -> int:
    return (byte >> 6) & 3


def get_reg(d_bit: int, w_bit: int, destination: bool, byte: int) -> str:
    target_bit_start = 3 if (bool(destination) == bool(d_bit)) else 0

    reg_bits = (byte >> target_bit_start) & 0b111
    key = (reg_bits << 1) | (w_bit & 1)

    return REG_LOOKUP[key]


def get_operands(chunk: bytes, operation: str) -> str:
    if operation == INTRUCTION_TYPE_TO_TEXT["MOV_REG_TO_REG"]:
        d_bit = (chunk[0] >> 1) & 1
        w_bit = chunk[0] & 1

        dst = get_reg(d_bit, w_bit, True, chunk[1])
        src = get_reg(d_bit, w_bit, False, chunk[1])

        return f"{dst}, {src}"

    raise Exception("unsupported operation")


def read_additional_chunks(file: BinaryIO, operation: str) -> Optional[bytes]:
    additional_chunk = None
    if operation == INTRUCTION_TYPE_TO_TEXT["MOV_REG_TO_REG"]:
        additional_chunk = file.read(1)
        mod = get_mod(additional_chunk[0])
        if mod == 0b11:
            pass
        elif mod == 0b00:
            r_m = additional_chunk[0] & 0b111
            if r_m == 0b110:
                additional_chunk += file.read(2)
        elif mod == 0b01:
            additional_chunk += file.read(1)
        elif mod == 0b10:
            additional_chunk += file.read(2)

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
            additional_chunk = read_additional_chunks(file, operation)

            if additional_chunk:
                chunk += additional_chunk

            operands = get_operands(chunk, operation)

            print(f"{operation} {operands}")


if __name__ == "__main__":
    main()
