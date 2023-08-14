#!/usr/bin/python3

# Copyright (C) 2015, Alexandrine Torrents <alexandrine.torrents at eurecom.fr>
#                     Mathieu Chevalier <mathieu.chevalier at eurecom.fr>
# All rights reserved.

import snap7
import argparse

GREEN = "\033[32;1m"
RED = "\033[31;1m"
CRESET = "\033[0m"

"""
For testing purposes only
"""


class MockS7(object):
    def __init__(self, string):
        self.content = bytearray(string)

    def read_area(self, area, dbnumber, start, size):
        return self.content[start:][:size]

    def write_area(self, area, dbnumber, start, data):
        size = len(data)
        self.content[start:start + size] = data

    def __repr__(self):
        return f"MockS7({repr(self.content)})"


def read_s7(s7, start_bit, bit_length):
    """
    start_bit = 4
    bit_length = 14
    |0|1|0|1|1|0|0|1| |0|1|1|1|0|1|0|0| |0|1|0|1|1|1|0|1|
             ^---start_bit = 4             ^---end_bit = 17 = start_bit + bit_length - 1

    """
    start_byte = start_bit // 8  # the byte where the first bit is located
    end_byte = (start_bit + bit_length - 1) // 8  # the byte where the last bit is located
    byte_length = end_byte - start_byte + 1  # the number of bytes to retrieve
    s = s7.read_area(snap7.types.areas['PA'], 0, start_byte, byte_length)

    relative_start_bit = start_bit - start_byte * 8  # all subsequent offsets are relative to the start of "s"
    print('===Outputs===')

    for current_bit_offset in range(relative_start_bit, relative_start_bit + bit_length):
        current_byte_offset = current_bit_offset // 8  # offset of the byte where the current bit is located
        bit_offset_in_current_byte = current_bit_offset % 8  # offset of the current bit inside the current byte (0-7)
        current_bit_value = (s[current_byte_offset] >> bit_offset_in_current_byte) & 1
        print(f"Output {current_bit_offset}: {current_bit_value}")


def write_s7(s7, start_bit, bit_string):
    """
    start_bit = 4
    bit_length = 14
    |0|1|0|1|1|0|0|1| |0|1|1|1|0|1|0|0| |0|1|0|1|1|1|0|1|
             ^---start_bit = 4             ^---end_bit = 17 = start_bit + bit_length - 1

    """
    assert all(i in "01" for i in bit_string)
    bit_length = len(bit_string)

    start_byte = start_bit // 8  # the byte where the first bit is located
    end_byte = (start_bit + bit_length - 1) // 8  # the byte where the last bit is located
    byte_length = end_byte - start_byte + 1  # the number of bytes to retrieve
    s = s7.read_area(snap7.types.areas['PA'], 0, start_byte, byte_length)

    relative_start_bit = start_bit - start_byte * 8  # all subsequent offsets are relative to the start of "s"

    for current_bit_offset, current_bit_value in zip(range(relative_start_bit, relative_start_bit + bit_length),
                                                     bit_string):
        current_byte_offset = current_bit_offset // 8  # offset of the byte where the current bit is located
        bit_offset_in_current_byte = current_bit_offset % 8  # offset of the current bit inside the current byte (0-7)
        if current_bit_value == "0":
            s[current_byte_offset] &= (1 << bit_offset_in_current_byte) ^ 0xFF
        elif current_bit_value == "1":
            s[current_byte_offset] |= (1 << bit_offset_in_current_byte)
        else:
            assert False
    s7.write_area(snap7.types.areas['PA'], 0, start_byte, s)
    print(GREEN + "[+] " + CRESET + str(bit_string) + " has been written correctly from address " + str(start_bit))


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Read or write on Siemens PLCs.')
    parser.add_argument('-a', metavar='<address>', type=int, required=True, dest='address',
                        help='Address from which data will be read/written')
    parser.add_argument('-m', metavar='<mode>', required=True, dest='mode', choices=['r', 'w'],
                        help='[r|w] Chosen mode: read or write on the PLC')
    parser.add_argument('-n', metavar='<number>', type=int, dest='number',
                        help='Number of data to read/write')
    parser.add_argument('-d', metavar='<data>', type=str, dest='data',
                        help='Data in binary to write (e.g. 1001)')
    parser.add_argument('ip_address', type=str)
    args = parser.parse_args()

    s7 = snap7.client.Client()
    s7.connect(args.ip_address, 0, 1)
    # s7 = MockS7("Lorem ipsum".encode())

    if args.mode == "r":
        if not args.number:
            parser.error("-n parameter misused or absent")
        read_s7(s7, args.address, args.number)
    elif args.mode == "w":
        data = args.data
        if len(data) == 0:
            parser.error("[-d] parameter misused or absent")
        if not all(i in "01" for i in data):
            parser.error("Data to be written shall only contain 0s and 1s")
        write_s7(s7, args.address, data)


if __name__ == "__main__":
    main()
