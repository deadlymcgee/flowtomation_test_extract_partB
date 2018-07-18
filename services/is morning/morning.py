#!/usr/bin/python3

"""
returns “true” if the input is a time prior to 12pm, otherwise “false”.
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

morning = custom_classes_part_2.Morning(input_time)
status, result_bytes = morning.get_results()

sys.stdout.buffer.write(result_bytes)
sys.exit(status)

