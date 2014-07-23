from ..annotations import LongParagraph
from .base import PageType


__all__ = ('BasicPage',)


class BasicPage(PageType):
    '''
    This is a page type that serves as a summary of common things that nearly
    all page can benefit from.
    '''

    annotations = [
        LongParagraph,
    ]

    def match(self, document):
        '''
        Always match.
        '''

        return 1
