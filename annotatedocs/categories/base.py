from ..annotations import LongParagraph
from ..metrics import MetricRequirementMixin, NodeType


__all__ = ('Category', 'BasicCategory', 'DefaultCategory',)


class Category(MetricRequirementMixin, object):
    name = None
    annotations = []

    def match(self, document):
        '''
        Returns a value between 0 and 1 on how good this category matches.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def get_annotations(self):
        return list(self.annotations)

    def apply_annotations(self, document):
        for annotation_class in self.get_annotations():
            document.apply_metrics(annotation_class.get_required_metrics())
            annotation = annotation_class()

            nodeset = document.nodeset.all()
            nodeset = annotation.limit(nodeset)
            annotation.apply(nodeset, document)


class BasicCategory(Category):
    '''
    This is a category that serves as a summary of common things that nearly
    all categories will need.
    '''

    annotations = [
        LongParagraph,
    ]
    required_metrics = Category.required_metrics + [
        NodeType,
    ]


class DefaultCategory(BasicCategory):
    '''
    This category will be applied when no other category reaches a minimum match value.
    '''

    name = 'no category found'

    def match(self, document):
        return 0
