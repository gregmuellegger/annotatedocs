from ..metrics import MetricRequirementMixin


__all__ = ('PageType',)


class PageType(MetricRequirementMixin, object):
    '''
    For every document in the documentation will be a page type determined that
    matches the kind of document. The page type then holds the checks that
    shall be applied against the document.

    That way you can have different checks which only will applied to the
    documents that they are relevant for.

    Page types can be grouped into bundles. See the ``Bundle`` class for more
    information.
    '''
    name = None
    checks = []

    def get_checks(self):
        '''
        This returns the checks that should be applied to the document which
        matches this page type.

        You can customize the behaviour based on the input gather during the
        ``match()`` call. This is usefull to apply different checks
        depending on how good the page type matched or if it contained this or
        that metric.
        '''
        return list(self.checks)

    def match(self, document):
        '''
        Returns a value between 0 and 1 on how good this page type matches.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def apply_checks(self, document):
        for check in self.get_checks():
            # We accept check classes and instances. We instantiate those
            # that were provided as classes.
            if isinstance(check, type):
                check = check()

            document.apply_metrics(check.get_required_metrics())

            nodeset = document.nodeset.all()
            nodeset = check.limit(nodeset)
            check.check(nodeset, document)
