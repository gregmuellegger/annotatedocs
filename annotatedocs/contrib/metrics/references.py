from urlparse import urlparse

from ...metrics import Metric, NodeType, require


__all__ = ('References',)


@require(NodeType)
class References(Metric):
    """
    Adds for every reference node the key 'refuri' with the target of the reference.

    It also adds the keys 'is_internal_ref' and 'is_external_ref'.
    ``is_internal_ref`` is set to ``True`` if the ``refuri`` points to another
    document inside the documentation, otherwise it's ``False``.
    ``is_external_ref`` is ``True`` if it's a link to a external resource, e.g.
    a website.
    """
    def limit(self, nodeset):
        return nodeset.filter(type='reference')

    def apply(self, node, document):
        is_internal_ref = False
        is_external_ref = False
        if 'refuri' in node.node.attributes:
            uri = node.node.attributes['refuri']
            node['refuri'] = uri

            result = urlparse(uri)
            # Consider it an external URI if it contains a domain.
            is_external_ref = bool(result.netloc)
            # Consider it an internal URI if it does not contain a domain.
            is_internal_ref = not bool(result.netloc)

            if result.scheme:
                node['uri_scheme'] = result.scheme
            if result.netloc:
                node['uri_netloc'] = result.netloc
            if result.path:
                node['uri_path'] = result.path
            if result.params:
                node['uri_params'] = result.params
            if result.query:
                node['uri_query'] = result.query
            if result.fragment:
                node['uri_fragment'] = result.fragment
            if result.username:
                node['uri_username'] = result.username
            if result.password:
                node['uri_password'] = result.password
            if result.hostname:
                node['uri_hostname'] = result.hostname
            if result.port:
                node['uri_port'] = result.port

        node['is_internal_ref'] = is_internal_ref
        node['is_external_ref'] = is_external_ref
