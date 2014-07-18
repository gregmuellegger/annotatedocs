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

    default_page_type = None
    minimum_page_type_match = 0.1

    def __init__(self, *args, **kwargs):
        self.bundles = []
        self.page_types = []

        for arg in args:
            if isinstance(arg, Bundle):
                self.bundles.append(arg)
            else:
                self.page_types.append(arg)

        self.default_page_type = kwargs.pop(
            'default_page_type',
            self.default_page_type)
        self.minimum_page_type_match = kwargs.pop(
            'minimum_page_type_match',
            self.minimum_page_type_match)

        if kwargs:
            raise TypeError(
                u'Unexpected keyword arguments: {}'.format(', '.join(kwargs)))

    def get_default_page_type(self, use_fallback=True):
        # We see if there was a ``default_page_type`` argument passed to the
        # constructor.
        default_page_type = self.default_page_type
        # If not we check the 'child' bundles if they have a default page type
        # set. Therefore we use the ``use_fallback=False`` keyword. Otherwise
        # we would get the ``fallback_default_page_type`` of the first bundle.
        if default_page_type is None:
            # Prefer bundles that were defined first.
            for bundle in self.bundles:
                bundle_default_page_type = bundle.get_default_page_type(
                    use_fallback=False)
                # The bundle has a default page type. So we use it.
                if bundle_default_page_type is not None:
                    default_page_type = bundle_default_page_type
                    break
        # In case we still don't have a default_page_type by now, we might get
        # an error from the ``Document`` class while determining the page type.
        return default_page_type

    def get_page_types(self):
        page_types = set(self.page_types)
        for bundle in self.bundles:
            page_types.update(bundle.get_page_types())
        return page_types
