from ...metrics import Metric, NodeType, require


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
