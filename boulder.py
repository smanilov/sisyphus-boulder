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
                # if the closing brace is after the for keyword then either
                # that scope is the for body, or it is contained by it
                if scopes[i][1] > index:
                        found = i
                        break

        if found is -1:
                print "could not find for loop body"
                continue

        i = found
        while i + 1 < len(scopes):
                i += 1
                if scopes[i][0] < index:
                        # scope containing for keyword
                        break
                if scopes[i][0] < scopes[found][0]:
                        # scope containing scope
                        found = i
                        continue
                if scopes[i][0] > scopes[found][1]:
                        # next scope
                        continue

        # see if the scope belongs to the for loop
        semicols = 0
        for i in range(index, scopes[found][0]):
                if text[i] is ";":
                        semicols += 1
        if not semicols is 2:
                # TODO: C++11 curly braces initialization
                print "could not find for loop body"
                print "index:", index, "found:", found, "semicols:", semicols
        else:
                for_loops.append((index, found))

        index = text.find(token, index + 1)

print "For loops:", for_loops

# Search for tokens
print "Detecting loops for unrolling..."
unroll_loop = [False] * len(for_loops)
for token in tokens:
        index = text.find(token)
        while not index is -1:
                found = -1
                for i in range(len(for_loops)):
                        s = scopes[for_loops[i][1]]
                        if s[0] < index and s[1] > index:
                                found = i
                                break

                # find nested loops that contain the token
                i = found
                while i + 1 < len(for_loops):
                        i += 1
                        f = scopes[for_loops[found][1]]
                        s = scopes[for_loops[i][1]]
                        if s[0] < index and s[1] > index:
                                # s contains the token
                                found = i

                        if s[0] < f[0] or s[1] > f[1]:
                                break

                if not found is -1:
                        found2 = -1
                        for i in range(found, len(for_loops)):
                                s = scopes[for_loops[i][1]]
                                # if index is out of the scope s
                                if s[0] > index or s[1] < index:
                                        found2 = i - 1
                                        break

                        # if index was in all of the nested scopes then
                        # make the inner-most for loop its owner
                        if found2 is -1:
                                found2 = len(for_loops) - 1

                        found = found2

                        print "Loop", found, "contains", index
                        unroll_loop[found] = True

                index = text.find(token, index + 1)

print "Unroll loops:", unroll_loop
