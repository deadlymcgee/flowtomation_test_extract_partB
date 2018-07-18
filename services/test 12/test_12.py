#!/usr/bin/python3

import sys
import json

"""
outputs a JSON message where the data payload does not match the output type
"""

status = 0
output = {
    "data": "the output"
}

output_bytes = json.dumps(output).encode("utf-8")
sys.stdout.buffer.write(
    output_bytes
)
sys.exit(status)
