# Chinese CCGbank conversion
# ==========================
# (c) 2008-2012 Daniel Tse <cncandc@gmail.com>
# University of Sydney

# Use of this software is governed by the attached "Chinese CCGbank converter Licence Agreement"
# supplied in the Chinese CCGbank conversion distribution. If the LICENCE file is missing, please
# notify the maintainer Daniel Tse <cncandc@gmail.com>.

from munge.io.guess_ptb import PTBGuesser, PrefacedPTBGuesser, YZPTBGuesser
from munge.io.guess_cptb import CPTBGuesser
from munge.io.guess_ccgbank import CCGbankGuesser

from munge.util.err_utils import warn, info
from munge.util.str_utils import padded_rsplit

class GuessReader(object):
    '''A reader which attempts to automatically guess the treebank
type based on the first bytes of the document (the context).'''
    def __init__(self, filename, guessers=(YZPTBGuesser, PrefacedPTBGuesser, CCGbankGuesser, PTBGuesser, CPTBGuesser), default=CCGbankGuesser):
        '''Initialises a GuessReader with a given set of guessers.'''
        self.guessers = list(guessers)
        self.default = default
        
        filename_only, index = padded_rsplit(filename, ':', 1)

        with open(filename_only, 'r') as file:
            self.preview = (file
                    .read(max(guessers, key=lambda guesser: guesser.bytes_of_context_needed())
                    .bytes_of_context_needed()))

        self.reader_class = self.determine_reader(self.preview)
        self.reader = self.reader_class(filename)
        
    def determine_reader(self, preview):
        '''Applies each of the guessers to the document, returning the corresponding reader class 
if a guesser matches.'''
        for guesser in self.guessers:
            if guesser.identify(preview):
                return guesser.reader_class()
        else:
            warn("determine_reader: No reader could be guessed given context ``%s''; assuming %s",
                preview,
                guesser.reader_class())
            return self.default.reader_class()
        
    def __iter__(self):
        '''Delegates to the found reader.'''
        for deriv in self.reader: yield deriv
        
    def __getitem__(self, index):
        '''Delegates to the guessed reader's __getitem__ method.'''
        return self.reader.__getitem__(index)
        
    def __setitem__(self, index, value):
        '''Delegates to the guessed reader's __setitem__ method.'''
        return self.reader.__setitem__(index, value)

    @property
    def derivs(self):
        return self.reader.derivs
        
    def __str__(self):
        return self.reader.__str__()
