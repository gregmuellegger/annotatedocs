from ... import PageType
from ..checks.longparagraph import LongParagraph
from ..checks.passivevoice import PassiveVoice


__all__ = ('BasicPage',)


class BasicPage(PageType):
    """
    This is a page type that serves as a summary of common things that nearly
    all page can benefit from.
    """

    checks = [
        LongParagraph,
        PassiveVoice,
    ]

    def match(self, document):
        '''
        Always match.
        '''

        return 1
