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
        nl_gen = fix_newlines(cvt_docstr_gen)
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
