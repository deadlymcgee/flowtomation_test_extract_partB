#!/usr/bin/env python3

import sys
import os
content_root = "/".join(os.path.dirname(os.path.realpath(__file__))
                        .split("/")[:-2])
sys.path.insert(
    0,
    content_root
)

import custom_classes_part_2


def main(directory):
    files = [
        os.path.join(directory, file) for file in
        os.listdir(directory)
    ]
    files_service = custom_classes_part_2.AppService()
    files_service.app_service_output["data"] = "\n".join(files)
    files_status, result_bytes = files_service.get_results()
    sys.stdout.buffer.write(result_bytes)
    return files_status


try:
    status = main(sys.argv[1])
except IndexError:
    sys.exit(1)

sys.exit(status)
