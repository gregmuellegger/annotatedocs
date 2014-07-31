def filter_nodes(nodes, check):
    result = []
    to_check = nodes[:]
    while to_check:
        current_node = to_check.pop()
        if check(current_node):
            if current_node not in result:
                result.append(current_node)
        to_check.extend(reversed(current_node.children))
    return result


def lookup(check):
    def _lookup(key, test_value):
        def _test_node(node):
            if key in node:
                return check(node[key], test_value)
            return False
        return _test_node
    return _lookup


def exists_lookup(key, test_value):
    def _test_node(node):
        exists = key in node
        # Return true if it exists. But only if we got ``True`` as lookup.
        if test_value:
            return exists
        # If the lookup was filter(key__exists=False) we want to invert the
        # result.
        else:
            return not exists
    return _test_node


class NodeSet(object):
    '''
    A node set has a root node and can be queried for it's children.

    An example::

        >>> nodeset = NodeSet(nodes)
        >>> all_paragraphs = nodeset.filter(type='paragraph')
        >>> print all_paragraphs
        [<paragraph: ...>, <paragraph: ...>]

    The lookups applied to the ``filter`` method apply to the node's data
    items. These are the objects that store the data that is added by the
    metric classes during analyzation.

    You can iterate over the nodeset to get the actual data out as single
    objects. Note that the nodeset will return
    ``annotatedocs.document.NodeData`` instances. To get to the actual
    docutil's ``Node`` instance, you have to access the node data's ``node``
    attribute, like this::

        >>> import docutils.nodes
        >>> nodeset = NodeSet(nodes)
        >>> nodedata = nodeset[0]
        >>> type(nodedata)
        <class 'annotatedocs.document.NodeData'>
        >>> isinstance(nodedata, docutils.nodes.Node)
        False
        >>> isinstance(nodedata.node, docutils.nodes.Node)
        True

    The API is heavily inspired by django's querysets.
    '''

    default_lookup_type = 'exact'

    # Methods given in lookup_types have a special signature.
    # They take three arguments:
    #
    #   ``key``
    #       The name of the keyword argument before the two underscores. So for
    #       ``.filter(foo__contains='bar')``, the key would be ``'foo'``.
    #
    #   ``test_value``
    #       The given value of the keyword argument. In the example above it
    #       would be ``'bar'``.
    #
    # They shall then based on those arguments return a callable that takes a
    # node and returns if the node meets a lookup specific criteria.

    lookup_types = {
        'exact': lookup(lambda a, b: a == b),
        'contains': lookup(lambda a, b: b in a),
        'gt': lookup(lambda a, b: a > b),
        'gte': lookup(lambda a, b: a >= b),
        'lt': lookup(lambda a, b: a < b),
        'lte': lookup(lambda a, b: a <= b),
        'exists': exists_lookup,
    }

    def __init__(self, root_nodes):
        self.root_nodes = list(root_nodes)
        self._filters = []

    def __repr__(self):
        nodes = list(self[:11])
        items = ', '.join(
            unicode(node.node.__class__.__name__)
            for node in nodes[:10])
        if len(nodes) > 10:
            items += ', ...'
        return '<{class_name}: len={count} [{items}]>'.format(
            class_name=self.__class__.__name__,
            count=self.count(),
            items=items)

    def _clone(self):
        cloned = self.__class__(self.root_nodes)
        cloned._filters = self._filters[:]
        return cloned

    def __getitem__(self, i):
        # TODO: optimize this.
        return list(self)[i]

    def all(self):
        return self._clone()

    def count(self):
        return len(self)

    def exists(self):
        # TODO: Optimize for performance and return True after the first
        # matching node was found.
        return self.count() >= 1

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
            filter_func = lookup_func(key, test_value)
            clone._filters.append(filter_func)

        return clone

    def subset(self):
        '''
        Make the currently filtered nodes the root nodes of a new nodeset.
        '''
        clone = self.__class__(list(self))
        return clone

    def first(self):
        '''
        Returns first item of nodeset or None if the nodeset is empty.
        '''

        try:
            return list(self)[0]
        except IndexError:
            return None

    def children(self):
        def is_children(node):
            return any(
                node in root_node.children
                for root_node in self.root_nodes)
        return self.filter(is_children)

    def annotate(self, message):
        '''
        Add a annotation to all selected nodes.
        '''
        for node in self:
            node.annotate(message)
        return self

    def values_list(self, *args, **kwargs):
        flat = kwargs.pop('flat', False)
        if not args:
            raise TypeError(u'You need to provide at least one value name.')
        if len(args) != 1 and flat:
            raise TypeError(u'The `flat` keyword can only be used if one value is specified.')
        if kwargs:
            raise TypeError(u'Unkown keyword arguments: {}'.format(kwargs.keys()))

        def get_values(node):
            if flat:
                return node[args[0]]
            return [node[key] for key in args]

        return [get_values(node) for node in self]

    def _accept_node(self, node):
        for filter_func in self._filters:
            if not filter_func(node):
                return False
        return True

    def _filter_nodes(self, nodes, check, include_children_of_matched=True):
        result = []
        to_check = nodes[:]
        while to_check:
            current_node = to_check.pop()
            matched = False
            if check(current_node):
                matched = True
                if current_node not in result:
                    result.append(current_node)
            if include_children_of_matched or matched:
                to_check.extend(reversed(current_node.children))
        return result

    def _evaluate(self, nodes):
        '''
        Resolves the configured nodeset into a list of nodes.
        '''
        return self._filter_nodes(nodes, self._accept_node)

    def __iter__(self):
        return iter(self._evaluate(self.root_nodes))
