from ...metrics import Metric, require
from .references import References


__all__ = ('EmailAddress',)


@require(References)
class EmailAddress(Metric):
    """
    Adds the ``'email_address'`` key to a node if it is a ``mailto:`` URI.
    """

    def limit(self, nodeset):
        return nodeset.filter(uri_scheme='mailto', uri_path__exists=True)

    def apply(self, node, document):
        node['email_address'] = node['uri_path']
