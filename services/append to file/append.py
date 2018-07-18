#!/usr/bin/python3

import sys
import json

string_to_append = json.loads(sys.stdin.read()).get("data")

with open(sys.argv[1], 'a') as output_file:
    output_file.write("{0}\n".format(string_to_append))

sys.exit()
