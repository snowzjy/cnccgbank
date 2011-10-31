from munge.proc.filter import Filter
from apps.cn.output import OutputPrefacedPTBDerivation
from munge.trees.traverse import nodes, leaves
from munge.penn.nodes import Leaf
from apps.cn.fix_utils import replace_kid
from munge.util.config import config

merge_verb_compounds = config.merge_verb_compounds

class Clean(Filter, OutputPrefacedPTBDerivation):
    def __init__(self, outdir):
        Filter.__init__(self)
        OutputPrefacedPTBDerivation.__init__(self, outdir)
        
    # def accept(self, root):
    #     return not any(node.tag.startswith('UCP') for node in nodes(root))
    #           
    # def accept_derivation(self, bundle):
    #     if self.accept(bundle.derivation):
    #         self.write_derivation(bundle)

    MergedTags = { 'VCD', 'VNV', 'VPT' }
    def accept_derivation(self, bundle):
        global merge_verb_compounds
        if merge_verb_compounds:
            for node in nodes(bundle.derivation):
                if node.tag in self.MergedTags:
                    replace_kid(node.parent, node, Leaf(node.tag, ''.join(kid.lex for kid in leaves(node)), node.parent))
        self.write_derivation(bundle)
            
    long_opt = 'clean'
    arg_names = 'OUTDIR'
