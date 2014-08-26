from ..annotations import Warning
from ..checks import Check
from .base import PageType


class HasTableOfContents(Check):
    def limit(self, nodeset):
        def is_toctree(node):
            return node.attributes.get('toctree') is not None
        return nodeset.filter(is_toctree)

    def check(self, nodeset, document):
        for node in nodeset:
            print node
        if nodeset.count() == 0:
            document.annotate(Warning('You don\'t have a TOC.'))
            document.structure.annotate(Warning('Global!'))
        (Warning('You don\'t have a TOC.'))


class Homepage(PageType):
    checks = PageType.checks + [
        HasTableOfContents
    ]
