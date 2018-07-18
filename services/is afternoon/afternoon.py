#!/usr/bin/python3

"""
returns “true” if the input is a time between 12pm and 6pm, otherwise “false”.
Exits with non zero return code and error message (stderr) if invalid time.
"""

import sys
import os

content_root = "/".join(os.path.dirname(os.path.realpath(__file__))
                        .split("/")[:-2])
sys.path.insert(
    0,
    content_root
)

import custom_classes_part_2

input_time = sys.stdin.read()
# input_time = "06/17/2018 10:32:10\n"

afternoon = custom_classes_part_2.Afternoon(input_time)
status, result_bytes = afternoon.get_results()

sys.stdout.buffer.write(result_bytes)
sys.exit(status)
