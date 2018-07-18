#!/usr/bin/python3

import sys

string_to_append = sys.stdin.read()
with open(sys.argv[1], 'a') as output_file:
    output_file.write(string_to_append)
