from .base import Metric


__all__ = ('NodeType',)


class NodeType(Metric):
    class_to_type = {
        'Text': 'text',
        'paragraph': 'paragraph',
        'title': 'headline',
        # TODO make this mapping complete.
    }

    def apply(self, node, data):
        class_name = node.__class__.__name__
        data['class_name'] = class_name
        data['type'] = self.class_to_type.get(class_name, class_name)
