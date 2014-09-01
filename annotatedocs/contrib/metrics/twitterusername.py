import re

from ...metrics import Metric, require
from .references import References


__all__ = ('TwitterUsername',)


@require(References)
class TwitterUsername(Metric):
    """
    Parses the links in the document and adds the ``'twitter_username'`` key
    for all URLs that point to a twitter user account.
    """

    twitter_url_re = re.compile('^https?://(?:www\.)?twitter\.com\.?/(?P<username>[^/]{1,15})')

    def limit(self, nodeset):
        return nodeset.filter(refuri__exists=True)

    def apply(self, node, document):
        username_match = self.twitter_url_re.search(node['refuri'])
        if username_match:
            username = username_match.groupdict().get('username')
            if username:
                node['twitter_username'] = username
