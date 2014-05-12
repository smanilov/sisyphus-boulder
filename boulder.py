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
print "Finding all scopes..."
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

# Find all for loops
print "Finding all for loops..."
for_loops = []
token = "for"
index = text.find(token)
while not index is -1:
        found = -1
        for i in range(len(scopes)):
                if scopes[i][1] > index:
                        found = i
                        break

        if not found is -1:
                semicols = 0
                for i in range(index, scopes[found][0]):
                        if text[i] is ";":
                                semicols += 1
                if not semicols is 2:
                        # TODO: C++11 curly braces initialization
                        print "could not find for loop body"
                else:
                        for_loops.append((index, found))

        index = text.find(token, index + 1)

print "For loops:", for_loops

# Search for tokens
print "Searching for tokens..."
unroll_loop = [False] * len(for_loops)
for token in tokens:
        print "Searching for token", token
        index = text.find(token)
        while not index is -1:
                print "Search for loop containing", index
                found = -1
                for i in range(len(for_loops)):
                        s = scopes[for_loops[i][1]]
                        if s[0] < index and s[1] > index:
                                found = i
                                break
                if not found is -1:
                        print "Loop", found, "contains", index
                        unroll_loop[found] = True
                index = text.find(token, index + 1)

print "Unroll loops:", unroll_loop
