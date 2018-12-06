#!/usr/bin/python

# Copyright (C) 2015, Alexandrine Torrents <alexandrine.torrents at eurecom.fr>
#                     Mathieu Chevalier <mathieu.chevalier at eurecom.fr>
# All rights reserved.

import snap7
import argparse

GREEN = "\033[32;1m"
RED = "\033[31;1m"
CRESET = "\033[0m"

# Parse command line arguments
parser = argparse.ArgumentParser(description='Read or write on Siemens PLCs.')
parser.add_argument('-a', metavar='<address>', type=int, nargs=1,
                   required=True, dest='address',
                   help='Address from which data will be read/written')
parser.add_argument('-m', metavar='<mode>', nargs=1, required=True,
                   dest='mode', choices=['r', 'w'],
                   help='[r|w] Chosen mode: read or write on the PLC')
parser.add_argument('-n', metavar='<number>', type=int, nargs=1,
                   required=True, dest='number',
                   help='Number of data to read/write')
parser.add_argument('-d', metavar='<data>', nargs=1, dest='data',
                   help='Data in binary to write (e.g. 1001)')
parser.add_argument('ip_address', nargs=1)
args = parser.parse_args()

HOST = args.ip_address[0]  # IP Address
PORT = 102                 #
MODE = args.mode[0]        # Read/Write
ADDRESS = args.address[0]  # Offset in bits
NUMBER = args.number[0]    # Number of bits to read/write

s7 = snap7.client.Client()
s7.connect(HOST, 0, 1)

def read():
    result = []
    output = []
    start = int(ADDRESS)/8
    offset = int(ADDRESS) % 8   # Where the start address is located in the byte
    offset_bis = 8 - offset       # How many bits are going to be read in the first byte
    new_number = int(NUMBER) - offset_bis  # New number to calculate the remaining bytes that need to be read
    if new_number <= 0:
        size = 1
    else:
        size = (new_number-1)/8 + 2
    s = s7.read_area(snap7.types.areas['DB'], 1, start, size)
    result = [bits[::-1] for bits in ['0' * (8 - len(bin(x)[2:])) + bin(x)[2:] for x in s]]
    for k in range(offset, min(8, offset + int(NUMBER))):
        output.append(result[0][k])  # to write the bits value of the first byte
        if 8 < offset + int(NUMBER):
            size_result = len(result)
            for l in range(1, size_result):
                for m in range(0, 8):
                    output.append(result[l][m])  # all the remaining bytes
    print '===Outputs==='
    for j in range(0, int(NUMBER)):
        print "Output " + str(int(ADDRESS) + j) + " : " + output[j]
    return None 

def write():
    DATA = args.data[0]        # Data to be written
    for i in DATA:
        if i != '0' and i != '1':
            parser.error("Data to be written shall only contain 0s and 1s")
    if len(DATA) == 0:
        parser.error("[-d] parameter misused or absent")
    if len(DATA) != NUMBER:
        parser.error("The number of bits to write, specified in [-n], is different from the size of the data given in [-d]")
    to_be_written = []
    data = []
    start = int(ADDRESS)/8
    offset = int(ADDRESS) % 8   # Where the start address is located in the byte
    offset_bis = 8-offset       # How many bits are going to be read in the first byte
    new_number = int(NUMBER) - offset_bis  # New number to calculate the remaining bytes that need to be read
    if new_number <= 0:
        size = 1
    else:
        size = (new_number-1)/8 + 2
    to_be_written.append(DATA[:offset_bis])
    to_be_written += [DATA[i + offset_bis: i + offset_bis + 8] for i in range(0, len(DATA) - offset_bis, 8)]
    s = s7.read_area(snap7.types.areas['DB'], 1, start, size)
    read_values = [bits[::-1] for bits in ['0' * (8 - len(bin(x)[2:])) + bin(x)[2:] for x in s]]
    if offset != 0:
        data.append(read_values[0][:offset])
    data += to_be_written[::]
    if new_number % 8 != 0:
        data.append(read_values[size - 1][new_number % 8:])
    if len(data[0]) != 8:
        data[0:2] = [''.join(data[0:2])]
    if len(data[-1]) != 8:
        data[len(data) - 2:len(data)] = [''.join(data[len(data) - 2:len(data)])]
    data1 = [int(byte[::-1], 2) for byte in data]
    data = bytearray(data1)
    s = s7.write_area(snap7.types.areas['DB'], 1, start, data)
    print GREEN + "[+] " + CRESET  + str(DATA) + " has been written correctly from address " + str(ADDRESS)
    return None

def main():
    if MODE == "r":
        read()
    elif MODE == "w":
        write()

if __name__ == "__main__":
    main()
