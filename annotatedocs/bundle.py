__all__ = ('Bundle',)


class Bundle(object):
    '''
    A bundle is a group of page types. It exists to make it easy to create the
    set of page types that can then be configured in the ``conf.py`` of a
    sphinx documentation project.

    You can make your own bundle of page types and specify it like this in your
    ``conf.py``::

        annotatedocs_bundle = 'myproject.annotations.project_bundle'

    TODO: Implement the conf.py support.
    '''

    default_page_types = None

    def __init__(self, *args, **kwargs):
        self.bundles = []
        self.page_types = []

        for arg in args:
            if isinstance(arg, Bundle):
                self.bundles.append(arg)
            else:
                self.page_types.append(arg)

        self.default_page_types = kwargs.pop(
            'default_page_types',
            self.default_page_types)

        if kwargs:
            raise TypeError(
                u'Unexpected keyword arguments: {}'.format(', '.join(kwargs)))

    def get_default_page_types(self, use_fallback=True):
        # We see if there was a ``default_page_types`` argument passed to the
        # constructor.
        default_page_types = self.default_page_types

        # If not we check the 'child' bundles if they have a default page type
        # set. Therefore we use the ``use_fallback=False`` keyword. Otherwise
        # we would get the ``fallback_default_page_type`` of the first bundle.
        if default_page_types is None:
            # Prefer bundles that were defined first.
            for bundle in self.bundles:
                bundle_default_page_types = bundle.get_default_page_types(
                    use_fallback=False)
                # The bundle has a default page type. So we use it.
                if bundle_default_page_types is not None:
                    default_page_types = bundle_default_page_types
                    break

        # In case we still don't have a default_page_types by now, the
        # analyzation will not be able to add any annotations.
        return default_page_types

    def get_page_types(self):
        page_types = set(self.page_types)
        for bundle in self.bundles:
            page_types.update(bundle.get_page_types())
        return page_types

    def match_page_type_class(self, page_type_class, document):
        page_type = page_type_class()
        document.apply_metrics(page_type.get_required_metrics())
        match = page_type.match(document=document)
        return page_type, match

    def is_sufficient_match(self, page_type, match):
        '''
        A page type will return a match between 0 and 1. That's what the API
        defines. This is the method to check if the match is ok enought so that
        we allow the analyzation of the document with the given page type.

        The default implementation states that every match which is not 0 is
        good enough. Customize this if you want to apply other criterias.
        '''
        return match > 0

    def determine_page_types(self, document):
        '''
        This is a good place to customize if you have defined your own bundle.
        '''

        matched_page_types = []
        for page_type_class in self.get_page_types():
            page_type, match = self.match_page_type_class(page_type_class,
                                                          document)
            if self.is_sufficient_match(page_type, match):
                matched_page_types.append(page_type)

        # We have no matched page type. So we apply the default page types,
        # without checking the match.
        if not matched_page_types:
            for page_type_class in self.get_default_page_types():
                page_type, match = self.match_page_type_class(page_type_class,
                                                              document)
                matched_page_types.append(page_type)

        return matched_page_types
