#! /usr/bin/python

from sishead import \
        print_usage, \
\
        read_source_file, \
        read_token_file, \
        read_unroll_factor, \
        read_output_file_name, \
\
        find_all_scopes, \
        find_all_for_loops, \
        detect_loops_for_unrolling, \
        gen_new_text, \
\
        write_output_file


\
              print_usage()

text        = read_source_file()
tokens      = read_token_file()
unrlfactor  = read_unroll_factor()
out_file    = read_output_file_name()

scopes      = find_all_scopes(text)
for_loops   = find_all_for_loops(text, scopes)
unroll_loop = detect_loops_for_unrolling(for_loops, tokens, text, scopes)
new_text    = gen_new_text(text, for_loops, scopes, unroll_loop, unrlfactor)
\
              write_output_file(new_text, out_file)
