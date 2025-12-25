import argparse
import sys

from decoder import (
    INSTRUCTION_TYPE_TO_OP,
    get_length_class,
    get_operands,
    get_operation,
    get_additional_chunks,
)
from simulation import SIM_REGISTERS, get_ip_register, set_ip_register, format_flags


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

        all_chunks = file.read()
        while True:
            current_ip, _ = get_ip_register()

            if current_ip >= len(all_chunks):
                break

            chunk = all_chunks[current_ip : current_ip + 1]
            length_class = get_length_class(chunk[0])
            additional_chunk = get_additional_chunks(all_chunks, length_class)

            if additional_chunk:
                chunk += additional_chunk

            set_ip_register(current_ip + len(chunk))
            operation = get_operation(chunk)
            operands = get_operands(chunk, operation, args.simulate)
            print(f"{INSTRUCTION_TYPE_TO_OP[operation]} {operands}")

        if args.simulate:
            print("\nFinal registers:")
            for key in SIM_REGISTERS:
                val = SIM_REGISTERS[key]
                print(f"\t{key}: {val:#06x} ({val})")
            flags_str = format_flags()
            if flags_str:
                print(f"\tflags: {flags_str}")


if __name__ == "__main__":
    main()
