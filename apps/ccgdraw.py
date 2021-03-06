# Chinese CCGbank conversion
# ==========================
# (c) 2008-2012 Daniel Tse <cncandc@gmail.com>
# University of Sydney

# Use of this software is governed by the attached "Chinese CCGbank converter Licence Agreement"
# supplied in the Chinese CCGbank conversion distribution. If the LICENCE file is missing, please
# notify the maintainer Daniel Tse <cncandc@gmail.com>.

import re, sys
from munge.util.list_utils import transpose
from apps.util.latex.table import sanitise_category
    
SpanRegex = re.compile(r'\S+')
def get_spans_of(words):
    for r in SpanRegex.finditer(words):
        yield r.span()
        
def get_spans_and_text_of(words):
    for r in SpanRegex.finditer(words):
        yield (r.span(), r.group())
    
ESCAPED_NEWLINE = '\\\\\n'
def comb_lines(lines):
    ret = []
    
    by_row = transpose(lines)
        
    cur_column = 0
    arrow_line = []
    cat_line = []
    
    while by_row[0]:
        (begin, end), arrow = by_row[0].pop(0), by_row[1].pop(0)
        category = by_row[2].pop(0)
        
        combinator = get_combinator_for_arrow(arrow)
        if not combinator: raise RuntimeError('Unknown combinator.')
        
        arrow_line.append( " & " * (begin - cur_column) )
        arrow_line.append( "\\%s{%d}" % (combinator, end-begin+1) )
        
        cat_line.append( " & " * (begin - cur_column) )
        cat_line.append( "\mc{%d}{%s}" % (end-begin+1, sanitise_category(category)) )

        cur_column = end
        
    arrow_line.append(ESCAPED_NEWLINE)
    cat_line.append(ESCAPED_NEWLINE)
     
    return ''.join(''.join(line) for line in (arrow_line, cat_line))
    
TailRegex = re.compile(r'-+(.*)')
tails = {
    '?': 'whatcomb',
    '>': 'fapply',
    '<': 'bapply',
    '>B': 'fcomp',
    '<B': 'bcomp',
    '>Bx': 'fxcomp',
    '<Bx': 'bxcomp',
    '>S': 'fsubst',
    '<S': 'bsubst',
    '>Sx': 'fxsubst',
    '<Sx': 'bxsubst',
    '>T': 'ftype',
    '<T': 'btype',
    'conj': 'conj',
    'conj1': 'conjone',
    'conj2': 'conjtwo',
    'topgap': 'topgap',
    'top': 'toptop',
    '': 'uline',
    '*': 'asterisk',
    'H': 'unhat',
}
def get_combinator_for_arrow(arrow):
    match = TailRegex.match(arrow)
    if match:
        tail_symbol = match.group(1)
        return tails[tail_symbol]
    
    return None
    
def word_lines(words):
    return (' & '.join('\\exm{%s}' % word for word in words) + '\\\\\n')
        

def process(lines, out=sys.stdout):
    lines.reverse()
    lines = [line for line in lines if line]
    
    words = lines.pop()
    spans = list(get_spans_of(words))
    
    out.write('\\deriv{%d}{' % len(spans))
    out.write( word_lines(words.split()) )
    
    while lines:
        arrows, categories = lines.pop(), lines.pop()
        arrow_spans = list(get_spans_and_text_of(arrows))
        category_spans = list(get_spans_and_text_of(categories))

        to_write = []
        for (cbegin, cend), category in category_spans:
            for (abegin, aend), arrow in arrow_spans:
                if abegin <= cbegin <= cend <= aend:
                    found = False
                    
                    for begin in xrange(len(spans)):
                        if found: break
                        
                        # Try the longest spans first (since they subsume smaller spans)
                        for end in xrange(len(spans)-1, -1, -1):
                            begin_index, end_index = spans[begin][0], spans[end][1]

                            if abegin <= begin_index <= end_index <= aend:
                                to_write.append( ((begin, end), arrow, category) )
                                
                                found = True
                                break # We want to break out of the begin,end nested loop
        
        out.write( comb_lines(to_write) )
        
    out.write('}')
        
if __name__ == '__main__':
    import sys
    from apps.ccgdraw import process
    inp = map(lambda e: e.rstrip(), sys.stdin.readlines())
    print ''.join("%% %s\n" % line for line in inp)
    process(inp)
