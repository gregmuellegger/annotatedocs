from .base import Metric


__all__ = ('NodeType',)


class NodeType(Metric):
    '''
    Tries to categorize nodes based on their docutils class.

    The goal is to make querying via the NodeSet easier.
    '''

    class_to_type = {
        'Text': 'text',
        'paragraph': 'paragraph',
        'title': 'headline',
        # TODO make this mapping complete.
    }

    content_types = ['headline', 'paragraph']

    def apply(self, node, data):
        class_name = node.__class__.__name__
        node_type = self.class_to_type.get(class_name, class_name)
        data['class_name'] = class_name
        data['type'] = node_type
        if node_type in self.content_types:
            data['is_content_type'] = True
