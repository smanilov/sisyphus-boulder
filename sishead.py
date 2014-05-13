import sys

def print_usage():
        # Print usage
        if len(sys.argv) < 5:
                format = """
Usage: %s source_file token_file unroll_factor output_file
        source_file
                a file containing c/c++/java source code
        token_file
                a file containing one token per line; These tokens
                are used to identify which loops to unroll - the ones
                containing any of the tokens in their bodies. Empty lines are
                ignored.
        unroll_factor
                the times each loop body should be copied in the output file
        output_file
                name of the output file
        """
                sys.exit(format % sys.argv[0])


def read_source_file():
        # Read source file
        source_file_name = sys.argv[1]
        source_file = open(source_file_name)
        return source_file.read()


def read_token_file():
        # Read token file; filter empty lines
        token_file_name = sys.argv[2]
        token_file = open(token_file_name)
        tokens_str = token_file.read()
        tokens = tokens_str.split('\n')
        return [t for t in tokens if t]


def read_unroll_factor():
        # Read source file
        unroll_factor = sys.argv[3]
        return int(unroll_factor)


def read_output_file_name():
        # Read source file
        return sys.argv[4]


def find_all_scopes(text):
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
        return scopes


def find_all_for_loops(text, scopes):
        # Find all for loops
        print "Finding all for loops..."
        for_loops = []
        token = "for"
        index = text.find(token)
        while not index is -1:
                found = -1
                for i in range(len(scopes)):
                        # if the closing brace is after the for keyword then
                        # either that scope is the for body, or it is contained
                        # by it
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
                        print "index:", index, "found:", found, \
                              "semicols:", semicols
                else:
                        for_loops.append((index, found))

                index = text.find(token, index + 1)
        return for_loops 


def detect_loops_for_unrolling(for_loops, tokens, text, scopes):
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

                                unroll_loop[found] = True

                        index = text.find(token, index + 1)
        return unroll_loop


def get_loop_iterator(mod):
        """Empty result indicates error."""
        i = mod.find("++")
        if not i is -1:
                if i is 0:
                        return mod[i + 2 : ]
                else:
                        return mod[ : i]

        i = mod.find("+=")
        if not i is -1:
                return mod[ : i]

        return ""


def get_loop_increment(mod):
        """-1 as a result indicates error."""
        if not mod.find("++") is -1:
                return 1

        i = mod.find("+=")
        if not i is -1:
                return int(mod[i + 2 : ])

        return -1


def gen_unroll_for_decl(old_for_declaration, itr, inc, unroll_factor):
        new_inc = inc* unroll_factor
        
        l = old_for_declaration.rfind(";")
        h = old_for_declaration.rfind(")")

        new_decl = old_for_declaration[ : l + 1]
        new_decl += " " + itr + " += " + str(new_inc)
        new_decl += old_for_declaration[h : ]
        return new_decl


import re

def gen_new_text(text, for_loops, scopes, unroll_loop, unroll_factor):
        print "Generating output..."

        ident = "        "
        new_line = "\n"

        new_text = ""
        offset = 0
        for i in range(len(unroll_loop)):
                if unroll_loop[i]:
                        new_text += text[offset : for_loops[i][0]]

                        # get loop body
                        s = scopes[for_loops[i][1]]
                        loop_body = text[s[0] + 2 + len(ident): s[1]]

                        # isolate loop modifier
                        l = text.rfind(";", for_loops[i][0], s[0])
                        h = text.rfind(")", for_loops[i][0], s[0])
                        mod = text[l + 1 : h]

                        # drop empty spaces
                        mod = re.sub(' ', '', mod)

                        itr = get_loop_iterator(mod)
                        inc = get_loop_increment(mod)

                        decl = text[for_loops[i][0] : scopes[for_loops[i][1]][0] + 1]
                        new_for = gen_unroll_for_decl(decl, itr, inc, unroll_factor)

                        new_text += new_for + new_line + ident
                        for j in range(unroll_factor):
                                new_text += re.sub(itr, itr + " + " + str(j), loop_body)

                        offset = scopes[for_loops[i][1]][1]

        new_text += text[offset : ]

        return new_text


def write_output_file(new_text, output_file_name):
        print "Writing to file..."
        f = open(output_file_name, "w")
        f.write(new_text)
        f.close()
