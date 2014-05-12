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

# Find all scopes
open_scope = "{"
close_scope = "}"
open_comment = ["/*", "//"]
close_comment = ["*/", "\n"]
open_string = "\""
close_string = "\""
not_close_string = "\\\""

in_comment = -1
in_string = False

scopes = []
stack = []
for i in range(len(text)):
        # handle strings and comments
        if not in_comment is -1:
                if text.startswith(close_comment[in_comment], i):
                        in_comment = -1
                continue  # don't check anything else
        if in_string:
                if text.startswith(close_string, i) and \
                   not text.startswith(not_close_string, i-1):
                        in_string = False
                continue  # don't check anything else
        # not in_string and not in_comment
        for j in range(len(open_comment)):
                if text.startswith(open_comment[j], i):
                        in_comment = j

        if text.startswith(open_string, i):
                in_string = True

        # actual scope building logic
        if text.startswith(open_scope, i):
                stack.append(i)
        if text.startswith(close_scope, i):
                try:
                        k = stack.pop()
                        scopes.append((k, i))
                except IndexError:
                        print "Unexpected closing bracket at index", i
                        raise

print "Scopes:", scopes

for token in tokens:
        print "Searching for token", token
        index = text.find(token)
        while not index is -1:
                print "Search for loop containing", index
                index = text.find(token, index + 1)
