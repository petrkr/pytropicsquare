
from tropicsquare.ports.micropython import TropicSquareMicroPython


def main():
    ts = TropicSquareMicroPython(None, None)
    print(ts.chipid)
    print(ts.riscv_fw_version)


if __name__ == "__main__":
    main()
