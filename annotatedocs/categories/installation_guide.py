from .base import GenericCategory
from ..metrics import NodeType, Stemmer


__all__ = ('InstallationGuide',)


class InstallationGuide(GenericCategory):
    required_metrics = [
        NodeType,
        Stemmer,
    ]

    def match(self, document):
        nodeset = document.nodeset.filter(stemmed_words__contains='install')
        print nodeset
        return 1
