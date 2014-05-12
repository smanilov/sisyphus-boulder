#! /usr/bin/python

import sys

if len(sys.argv) < 2:
        sys.exit("Usage: %s input_file" % sys.argv[0])

input_file_name = sys.argv[1]
input_file = open(input_file_name)
text = input_file.read()

print text

