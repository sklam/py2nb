from __future__ import absolute_import, division, print_function

import tokenize


def read(filename):
    """
    Read a regular Python file with special formatting and performance
    preprocessing on it.  The result is a string that conforms to the IPython
    notebook version 3 python script format.
    """
    with open(filename, 'rb') as fin:
        token_gen = tokenize.tokenize(fin.readline)
        cvt_docstr_gen = convert_toplevel_docstring(token_gen)
        inlined_gen = inline_code_fragement(cvt_docstr_gen)
        nl_gen = fix_newlines(inlined_gen)
        out = list(nl_gen)

    formatted = tokenize.untokenize(out).decode('utf-8')
    return fix_empty_lines(formatted)


# =============================================================================
#                                   Helpers
# =============================================================================

def convert_toplevel_docstring(tokens):
    for token in tokens:
        # For each string
        if token.type == tokenize.STRING:
            text = token.string
            # Must be a docstring
            if text.startswith('"""') or text.startswith("'''"):
                startline, startcol = token.start
                # Starting column MUST be 0
                if startcol == 0:
                    endline, endcol = token.end
                    lines = ['# ' + line
                             for line in text.strip('"\' \n').split('\n')]
                    text = '\n'.join(lines)
                    fmt = '# <markdowncell>\n{0}\n# <codecell>'.format(text)
                    yield tokenize.TokenInfo(type=tokenize.COMMENT,
                                             start=(startline, startcol),
                                             end=(endline, endcol),
                                             string=fmt,
                                             line='#')
                    # To next token
                    continue
        # Return untouched
        yield token


def inline_code_fragement(tokens):
    got_inline_tag = False
    got_function = False
    got_first_indent = False
    indent_level = None

    for token in tokens:
        if not got_inline_tag:
            # Search for @inline tag
            if token.type == tokenize.COMMENT:
                text = token.string.lstrip('#').strip()
                if text == '@inline':
                    got_inline_tag = True
                    # Eat it
                    continue

        elif not got_function:
            # Modify next function definition
            if token.type == tokenize.NAME and token.string == 'def':
                # Got function definition
                got_function = True
                # Eat it
                continue

        elif not got_first_indent:
            # Find first indent
            if token.type == tokenize.INDENT:
                got_first_indent = True
                indent_level = token.end[1]
            # Eat everyting in between
            continue

        else:
            if token.type == tokenize.DEDENT and token.start[1] == 0:
                # Dedent to first column
                # Reset
                got_inline_tag = False
                got_function = False
                got_first_indent = False
                indent_level = None
                # Eat it
                continue
            else:
                string = token.string
                if token.type == tokenize.INDENT:
                    string = string[indent_level:]
                start = (token.start[0], max(0, token.start[1] - indent_level))
                end = (token.end[0], max(0, token.end[1] - indent_level))
                token = tokenize.TokenInfo(type=token.type,
                                           start=start,
                                           end=end,
                                           string=string,
                                           line=token.line[indent_level:])
                yield token
                continue

        yield token


def fix_newlines(tokens):
    first = True
    curline = 1
    for token in tokens:
        if first:
            first = False
            curline = token.end[0] + 1
        else:
            # Fill NEWLINE token in between
            while curline < token.start[0]:
                yield tokenize.TokenInfo(type=tokenize.NEWLINE,
                                         string='\n',
                                         start=(curline, 0),
                                         end=(curline, 0),
                                         line='\n', )
                curline += 1

            curline = token.end[0] + 1
        yield token


def fix_empty_lines(text):
    def gen():
        for line in text.splitlines():
            if not line.strip():
                # Empty line
                yield ''
            else:
                yield line

    return '\n'.join(gen())
