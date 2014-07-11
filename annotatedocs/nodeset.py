def filter_nodes(node, check):
    result = []
    to_check = [node]
    while to_check:
        current_node = to_check.pop()
        if check(current_node):
            result.append(current_node)
        to_check.extend(reversed(current_node.children))
    return result


class NodeSet(object):
    '''
    A node set has a root node and can be queried for it's children.

    An example::

        >>> nodeset = NodeSet(node)
        >>> all_paragraphs = nodeset.filter(type='paragraph')
        >>> print all_paragraphs
        [<paragraph: ...>, <paragraph: ...>]

    It is inspired by django's querysets.
    '''

    def __init__(self, document):
        self.document = document
        self.node = self.document.node

        self._filters = []

    def _clone(self):
        cloned = self.__class__(self.document)
        cloned._filters = self._filters[:]
        return cloned

    def all(self):
        return self._clone()

    def filter(self, *args, **kwargs):
        clone = self._clone()
        type = kwargs.pop('type')
        if type:
            clone._filters.append(
                self._get_type_filter(type))

        # Reject unkown kwargs.
        if kwargs:
            raise TypeError(
                'Unexpected keyword arguments: {kwargs}'.format(
                    kwargs=', '.join(kwargs)))

        clone._filters.extend(args)
        return clone

    def _get_type_filter(self, type):
        def type_filter(node):
            return node.__class__.__name__ == type
        return type_filter

    def _accept_node(self, node):
        for filter_func in self._filters:
            if not filter_func(node):
                return False
        return True

    def _evaluate(self, node):
        '''
        Resolves the configured nodeset into a list of nodes.
        '''
        return filter_nodes(node, self._accept_node)

    def __iter__(self):
        if not hasattr(self, '_result_cache'):
            self._result_cache = list(self._evaluate(self.node))
        for node in self._result_cache:
            yield node

    def annotate(self, annotation):
        '''
        Add a annotation to all selected nodes.
        '''
        for node in self:
            self.document.add_annotation(node, annotation)
        return self
