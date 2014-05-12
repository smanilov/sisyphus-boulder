#! /usr/bin/python

import sys

# Print usage
if len(sys.argv) < 3:
        format = """
Usage: %s source_file token_file
        source_file
                a file containing c/c++/java source code
        token_file
                a file containing one token per line; These tokens
                are used to identify which loops to unroll - the ones
                containing any of the tokens in their bodies. Empty lines are
                ignored.
"""
        sys.exit(format % sys.argv[0])

# Read source file
source_file_name = sys.argv[1]
source_file = open(source_file_name)
text = source_file.read()

# Read token file; filter empty lines
token_file_name = sys.argv[2]
token_file = open(token_file_name)
tokens_str = token_file.read()
tokens = tokens_str.split('\n')
tokens = [t for t in tokens if t]

for token in tokens:
        print "Searching for token", token
        index = text.find(token)
        while not index is -1:
                print "Search for loop containing", index
                index = text.find(token, index + 1)
