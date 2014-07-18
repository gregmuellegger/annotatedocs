from ..annotations import LongParagraph
from ..metrics import MetricRequirementMixin, NodeType


__all__ = ('PageType', 'BasicPage', 'DefaultPage',)


class PageType(MetricRequirementMixin, object):
    '''
    For every document in the documentation will be a page type determined that
    matches the kind of document. The page type then holds the annotations that
    shall be checked against the document.

    That way you can have different annotations which only will only applied
    for the documents that they are relevant for.

    Page types can be grouped into bundles. See the ``Bundle`` class for more
    information.
    '''
    name = None
    annotations = []

    def get_annotations(self):
        '''
        This returns the annotations that should be checked and applied to the
        document which matches this page type.

        You can customize the behaviour based on the input gather during the
        ``match()`` call. This is usefull to apply different annotations
        depending on how good the page type matched or if it contained this or
        that metric.
        '''
        return list(self.annotations)

    def match(self, document):
        '''
        Returns a value between 0 and 1 on how good this page type matches.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def apply_annotations(self, document):
        for annotation in self.get_annotations():
            # We accept annotation classes and instances. We instantiate those
            # that were provided as classes.
            if isinstance(annotation, type):
                annotation = annotation()

            document.apply_metrics(annotation.get_required_metrics())

            nodeset = document.nodeset.all()
            nodeset = annotation.limit(nodeset)
            annotation.apply(nodeset, document)


class BasicPage(PageType):
    '''
    This is a page type that serves as a summary of common things that nearly
    all page types will need.
    '''

    annotations = [
        LongParagraph,
    ]
    required_metrics = PageType.required_metrics + [
        NodeType,
    ]


class DefaultPage(BasicPage):
    '''
    This is the default default-page-type. It will be applied to a document when
    no other page type reaches a minimum match threshold. The default page type
    can be customized on a per project basis.
    '''

    name = 'no page type found'

    def match(self, document):
        return 0
