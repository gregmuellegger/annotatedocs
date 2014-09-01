from .base import PageType


__all__ = ('NamedPage',)


class NamedPage(PageType):
    """
    This page type always matches to the document name given in the init
    method. It's useful to explicitly applying a set of checks onto a specific
    document.

    Example::

        bundle = Bundle(
            NamedPage('installation_guide', [InstallationGuideCheck])

    This will apply the ``InstallationGuideCheck`` to the
    ``installtion_guide.rst`` file.
    """

    def __init__(self, document_name, checks):
        self.document_name = document_name
        self.checks = checks
        super(NamedPage, self).__init__()

    @property
    def name(self):
        return self.document_name

    def match(self, document):
        return int(document.name == self.document_name)
