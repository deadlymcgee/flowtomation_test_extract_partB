#!/usr/bin/env python3

# apply a regular expression to each incoming lines
# only print those that match

import sys
import re
import os
import json
content_root = "/".join(os.path.dirname(os.path.realpath(__file__))
                        .split("/")[:-2])
sys.path.insert(
    0,
    content_root
)

import custom_classes_part_2


def main(regex):
    lines = json.loads(sys.stdin.read()).get("data")
    lines = [line for line in lines.split("\n") if len(line) > 0]

    matched_lines = [
        line for line in lines if re.search(regex, line)
    ]

    filter_service = custom_classes_part_2.AppService()
    filter_service.app_service_output["data"] = "\n".join(matched_lines)
    filter_status, result_bytes = filter_service.get_results()
    sys.stdout.buffer.write(result_bytes)
    return filter_status


try:
    status = main(sys.argv[1])

except IndexError:
    sys.exit(1)

sys.exit(status)
