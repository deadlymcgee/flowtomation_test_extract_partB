#!/usr/bin/python3

import sys
import json

"""
outputs a JSON message missing the 'data' field
"""

status = 0
output = {
    "monkeys": "the output"
}

output_bytes = json.dumps(output).encode("utf-8")
sys.stdout.buffer.write(
    output_bytes
)
sys.exit(status)
