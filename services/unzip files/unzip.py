#!/usr/bin/env python3

# open up zip files...


import sys
import zipfile
import os
import json
content_root = "/".join(os.path.dirname(os.path.realpath(__file__))
                        .split("/")[:-2])
sys.path.insert(
    0,
    content_root
)

import custom_classes_part_2


def main():
    lines = json.loads(sys.stdin.read()).get("data")
    lines = [line for line in lines.split('\n') if len(line) > 0]
    file_list = []

    for file in lines:
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as my_zip:
                for name in my_zip.namelist():
                    file_list.append(name)

    unzip_service = custom_classes_part_2.AppService()
    unzip_service.app_service_output["data"] = "\n".join(file_list)
    unzip_status, result_bytes = unzip_service.get_results()
    sys.stdout.buffer.write(result_bytes)
    return unzip_status


status = main()
sys.exit(status)

