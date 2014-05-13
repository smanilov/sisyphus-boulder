#! /usr/bin/python

from sishead import \
        print_usage, \
        read_source_file, \
        read_token_file, \
        find_all_scopes, \
        find_all_for_loops, \
        detect_loops_for_unrolling

print_usage()
text = read_source_file()
tokens = read_token_file()
scopes = find_all_scopes(text)

print "Scopes:", scopes
for_loops = find_all_for_loops(text, scopes)

print "For loops:", for_loops
unroll_loop = detect_loops_for_unrolling(for_loops, tokens, text, scopes)

print "Unroll loops:", unroll_loop
