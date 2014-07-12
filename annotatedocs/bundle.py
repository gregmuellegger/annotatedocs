__all__ = ('Bundle',)


class Bundle(object):
    '''
    A bundle is a group of categories. It exists to make it easy to create the
    set of categories that can then be configured in the ``conf.py`` of a
    sphinx documentation project.

    You can make your own bundle of categories and specify it like this in your
    ``conf.py``::

        annotatedocs_bundle = 'myproject.annotations.project_bundle'

    TODO: Implement the conf.py support.
    '''

    default_category = None
    minimum_category_match = 0.1

    def __init__(self, *args, **kwargs):
        self.bundles = []
        self.categories = []

        for arg in args:
            if isinstance(arg, Bundle):
                self.bundles.append(arg)
            else:
                self.categories.append(arg)

        self.default_category = kwargs.pop(
            'default_category',
            self.default_category)
        self.minimum_category_match = kwargs.pop(
            'minimum_category_match',
            self.minimum_category_match)

        if kwargs:
            raise TypeError(
                u'Unexpected keyword arguments: {}'.format(', '.join(kwargs)))

    def get_default_category(self, use_fallback=True):
        # We see if there was a ``default_category`` argument passed to the
        # constructor.
        default_category = self.default_category
        # If not we check the 'child' bundles if they have a default category
        # set. Therefore we use the ``use_fallback=False`` keyword. Otherwise
        # we would get the ``fallback_default_category`` of the first bundle.
        if default_category is None:
            # Prefer bundles that were defined first.
            for bundle in self.bundles:
                bundle_default_category = bundle.get_default_category(
                    use_fallback=False)
                # The bundle has a default category. So we use it.
                if bundle_default_category is not None:
                    default_category = bundle_default_category
                    break
        # In case we still don't have a default_category by now, we might get
        # an error from the ``Document`` class while determining the category.
        return default_category

    def get_categories(self):
        categories = set(self.categories)
        for bundle in self.bundles:
            categories.update(bundle.get_categories())
        return categories
