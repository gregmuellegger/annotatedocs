from .base import Metric


__all__ = ('NodeType',)


class NodeType(Metric):
    """
    Tries to categorize nodes based on their docutils class.

    The goal is to make querying via the NodeSet easier.
    """

    class_to_type = {
        'Text': 'text',
        # TODO: make this mapping complete.
    }

    content_types = ['title', 'paragraph']

    # TODO: Integrate all attributes.
    # Name of node attributes that should be added to the node data.
    attributes = [
        'language',
    ]

    def apply(self, node, document):
        class_name = node.node.__class__.__name__
        node_type = self.class_to_type.get(class_name, class_name)
        node['class_name'] = class_name
        node['type'] = node_type
        if node_type in self.content_types:
            node['is_content_type'] = True

        if hasattr(node.node, 'attributes'):
            for attribute_name in self.attributes:
                attrs = node.node.attributes
                if attribute_name in attrs:
                    node[attribute_name] = attrs[attribute_name]
