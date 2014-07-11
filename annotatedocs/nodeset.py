def filter_nodes(node, check):
    result = []
    to_check = [node]
    while to_check:
        current_node = to_check.pop()
        if check(current_node):
            result.append(current_node)
        to_check.extend(reversed(current_node.children))
    return result


def lookup(check):
    def _lookup(document, key, test_value):
        def _test_node(node):
            data = document[node]
            if key in data:
                return check(data[key], test_value)
            return False
        return _test_node
    return _lookup


def exists_lookup(document, key, test_value):
    def _test_node(node):
        data = document[node]
        return key in data
    return _test_node


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

    default_lookup_type = 'exact'

    # Methods given in lookup_types have a special signature.
    # They take three arguments:
    #   ``document``
    #
    #   ``key``: The name of the keyword argument before the two underscores.
    #       So for ``.filter(foo__contains='bar')``, the key would be 'foo'.
    #
    #   ``test_value``: The given value of the keyword argument. In the example
    #       above it would be ``'bar'``.
    #
    # They shall then return based on those arguments return a callable that
    # takes a node and returns if the node meets a lookup specific criteria.

    lookup_types = {
        'exact': lookup(lambda a, b: a == b),
        'contains': lookup(lambda a, b: b in a),
        'gt': lookup(lambda a, b: a > b),
        'gte': lookup(lambda a, b: a >= b),
        'lt': lookup(lambda a, b: a < b),
        'lte': lookup(lambda a, b: a <= b),
        'exists': exists_lookup,
    }

    def __init__(self, document):
        self.document = document
        self.node = self.document.node

        self._filters = []

    def __repr__(self):
        items = ', '.join(unicode(node) for node in list(self))
        return '<{class_name}: len={count} [{items}]>'.format(
            class_name=self.__class__.__name__,
            count=self.count(),
            items=items)

    def _clone(self):
        cloned = self.__class__(self.document)
        cloned._filters = self._filters[:]
        return cloned

    def all(self):
        return self._clone()

    def count(self):
        return len(self)

    def __len__(self):
        return list(self.__iter__()).__len__()

    def filter(self, *args, **kwargs):
        '''
        You can provide positional arguments which must be callables. The
        callback should take one argument, a node, and returns ``True`` or
        ``False`` to indicate if the node should be included in the returned
        nodeset or not.

        Keyword arguments check the given value against a key in the node's
        data. So for example::

            nodeset.filter(class_name='paragraph')

        Will only return nodes which have the key ``'class_name'`` set in the
        node data and it is set to ``'paragraph'``.
        '''

        clone = self._clone()

        clone._filters.extend(args)
        for lookup, test_value in kwargs.items():
            if '__' in lookup:
                key, lookup_type = lookup.split('__', 1)
            else:
                key = lookup
                lookup_type = self.default_lookup_type

            if lookup_type not in self.lookup_types:
                raise TypeError(u'Unkown lookup: {}'.format(lookup))

            lookup_func = self.lookup_types[lookup_type]
            filter_func = lookup_func(self.document, key, test_value)
            clone._filters.append(filter_func)

        return clone

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
