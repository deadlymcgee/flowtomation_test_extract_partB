#!/usr/bin/python3

import sys
import datetime
import os


content_root = "/".join(os.path.dirname(os.path.realpath(__file__))
                        .split("/")[:-2])
sys.path.insert(
    0,
    content_root
)
python_path = sys.path
import custom_classes_part_2


# date_time_format = sys.stdin.read()
# date_time_format = "%d/%m/%Y %H:%M:%S"
date_time_format = sys.argv[1]
get_date_time = custom_classes_part_2.AppService()
get_date_time.app_service_output["data"] = datetime.datetime.now()\
    .strftime(date_time_format.rstrip())
status, result_bytes = get_date_time.get_results()

sys.stdout.buffer.write(result_bytes)
sys.exit(status)
