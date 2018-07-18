#!/usr/bin/python3

"""

"""

import sys
import os
import json

content_root = "/".join(os.path.dirname(os.path.realpath(__file__))
                        .split("/")[:-2])
sys.path.insert(
    0,
    content_root
)

import custom_classes_part_2

# input_string = sys.stdin.read()
# input_string_bytes = b'{"data": "25/06/2018 14:52:00"}'
# input_string = input_string_bytes.decode("utf-8")

input_string = " ".join(sys.argv[1:])


py_echo = custom_classes_part_2.AppService()
# py_echo.app_service_output = json.loads(input_string)
py_echo.app_service_output["data"] = input_string

status, output_string_bytes = py_echo.get_results()

sys.stdout.buffer.write(output_string_bytes)


sys.exit(status)
