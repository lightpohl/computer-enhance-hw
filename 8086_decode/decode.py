import sys

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


def get_operation(chunk: bytes) -> str:
    byte = chunk[0]
    op_code = byte >> 2

    if op_code == int("100010", 2):
        return "mov"
    else:
        raise Exception("unsupported op_code")


def get_d_bit(chunk: bytes) -> int:
    return (chunk[0] >> 1) & 1


def get_w_bit(chunk: bytes) -> int:
    return chunk[0] & 1


def get_reg(d_bit: int, w_bit: int, destination: bool, byte: int) -> str:
    target_bit_start = 3 if (bool(destination) == bool(d_bit)) else 0

    reg_bits = (byte >> target_bit_start) & 0b111
    key = (reg_bits << 1) | (w_bit & 1)

    return REG_LOOKUP[key]


def get_operands(chunk: bytes) -> str:
    d_bit = get_d_bit(chunk)
    w_bit = get_w_bit(chunk)

    dst = get_reg(d_bit, w_bit, True, chunk[1])
    src = get_reg(d_bit, w_bit, False, chunk[1])

    return f"{dst}, {src}"


def main():
    file_path = sys.argv[1]

    if not file_path:
        print("no file_path provided")
        sys.exit(1)

    with open(file_path, "rb") as file:
        print(f"; {file.name}:")
        print("bits 16")

        while True:
            chunk = file.read(2)

            if not chunk:
                break

            operation = get_operation(chunk)
            operands = get_operands(chunk)

            print(f"{operation} {operands}")


if __name__ == "__main__":
    main()
