from ..utils import instantiate


__all__ = ('Bundle',)


class Bundle(object):
    """
    A bundle is a group of page types. It exists to make it easy to create the
    set of page types that can then be configured in the ``conf.py`` of a
    sphinx documentation project.

    You can make your own bundle of page types and specify it like this in your
    ``conf.py``::

        annotatedocs_bundle = 'myproject.docchecks.project_bundle'

    TODO: Implement the conf.py support.
    """

    fallback_page_types = None

    def __init__(self, *args, **kwargs):
        self.bundles = []
        self.page_types = []

        for arg in args:
            if isinstance(arg, Bundle):
                self.bundles.append(arg)
            else:
                # Accept instance or class.
                arg = instantiate(arg)
                self.page_types.append(arg)

        self.fallback_page_types = kwargs.pop(
            'fallback_page_types',
            self.fallback_page_types)

        if kwargs:
            raise TypeError(
                u'Unexpected keyword arguments: {}'.format(', '.join(kwargs)))

    def get_fallback_page_types(self, use_fallback=True):
        # We see if there was a ``fallback_page_types`` argument passed to the
        # constructor.
        fallback_page_types = self.fallback_page_types

        # If not we check the 'child' bundles if they have a fallback page type
        # set. Therefore we use the ``use_fallback=False`` keyword. Otherwise
        # we would get the ``fallback_fallback_page_type`` of the first bundle.
        if fallback_page_types is None:
            # Prefer bundles that were defined first.
            for bundle in self.bundles:
                bundle_fallback_page_types = bundle.get_fallback_page_types(
                    use_fallback=False)
                # The bundle has a fallback page type. So we use it.
                if bundle_fallback_page_types is not None:
                    fallback_page_types = bundle_fallback_page_types
                    break

        # In case we still don't have a fallback_page_types by now, the
        # analyzation will not be able to apply any checks.
        return fallback_page_types or []

    def get_page_types(self):
        page_types = set(self.page_types)
        for bundle in self.bundles:
            page_types.update(bundle.get_page_types())
        return page_types

    def get_page_type_match(self, page_type, document):
        document.apply_metrics(page_type.get_required_metrics())
        return page_type.match(document=document)

    def should_select_page_type(self, page_type, document, match):
        """
        A page type will return a match between 0 and 1. That's what the API
        defines. This is the method to check if the match is ok enough so that
        we allow the analyzation of the document with the given page type.

        The default implementation states that every match which is not 0 is
        good enough. Customize this if you want to apply other criterias. You
        can even ignore the ``match`` alltogether and hardcode if a page type
        is accepted for the given document.

        Return ``True`` if the page type should be selected.
        """
        return match > 0

    def determine_page_types(self, document):
        """
        This is a good place to customize if you have defined your own bundle
        and want to get crazy about how the categories are matched to the
        documents.
        """

        matched_page_types = []
        for page_type in self.get_page_types():
            match = self.get_page_type_match(page_type, document)
            if self.should_select_page_type(page_type, document, match):
                matched_page_types.append(page_type)

        # We have no matched page type. So we apply the fallback page types,
        # without checking the match.
        if not matched_page_types:
            for page_type in self.get_fallback_page_types():
                match = self.get_page_type_match(page_type, document)
                matched_page_types.append(page_type)

        return matched_page_types
