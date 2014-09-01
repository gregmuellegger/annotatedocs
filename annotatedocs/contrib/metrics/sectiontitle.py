from ...metrics import Metric, NodeType, require
from .stemmer import Stemmer


__all__ = ('SectionTitle',)


@require(NodeType)
class SectionTitle(Metric):
    """
    Add a ``'title'`` key to the node data containing the node that represents
    the title for this section.
    """

    def limit(self, nodeset):
        return nodeset.filter(type='section')

    def apply(self, node, document):
        titles = node.nodeset.filter(type='title')
        # Check that the title is the actual title for this section and not
        # deeply nested.
        titles = titles.filter(lambda n: n.parent is node)
        title = titles.first()
        if title:
            node['title'] = title


@require(NodeType, SectionTitle, Stemmer)
class SectionTitleContainsKeywords(Metric):
    """
    Checks if a section title contains on of the keywords specified in the
    ``keywords`` attribute. If that is the case, the section will get a flag
    set to ``True``. The name of the key in which this is stored is specified
    with the ``flag_name`` attribute.

    This class is only useful when subclassed and the ``keywords`` and
    ``flag_name`` attributes are overriden.
    """
    keywords = []
    flag_name = None

    def __init__(self, *args, **kwargs):
        super(SectionTitleContainsKeywords, self).__init__(*args, **kwargs)
        self.stemmed_keywords = set(Stemmer.stem(' '.join(self.keywords)))
        assert self.flag_name, "`flag_name` attribute is not set."

    def title_contains_one_keyword(self, node):
        title = node['title']
        for word in title['stemmed_words']:
            if word in self.stemmed_keywords:
                return True

    def limit(self, nodeset):
        """
        Only return sections with a title that contains a keyword that
        indicates that this is a section that talks about dependencies.
        """
        nodeset = nodeset.filter(type='section', title__exists=True)
        return nodeset.filter(self.title_contains_one_keyword)

    def apply(self, node, document):
        node[self.flag_name] = True
