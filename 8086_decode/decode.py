import argparse
import sys

from shared import (
    INSTRUCTION_TYPE_TO_OP,
    get_length_class,
    get_operands,
    get_operation,
    read_additional_chunks,
)
from simulation import SIM_REGISTERS


def main():
    parser = argparse.ArgumentParser(prog="8086 Decoder")
    parser.add_argument("-f", "--file")
    parser.add_argument("-s", "--simulate", action="store_true")
    args = parser.parse_args()

    if args.file is None:
        print("no --file provided")
        sys.exit(1)

    with open(args.file, "rb") as file:
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
            operands = get_operands(chunk, operation, args.simulate)
            print(f"{INSTRUCTION_TYPE_TO_OP[operation]} {operands}")

        if args.simulate:
            print("\nFinal registers:")
            for key in SIM_REGISTERS:
                print(f"\t{key}: {SIM_REGISTERS[key]:#x} ({SIM_REGISTERS[key]})")


if __name__ == "__main__":
    main()
