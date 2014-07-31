from annotatedocs.bundle import Bundle
from annotatedocs.annotations import LongSection
from annotatedocs.page_types import PageType, BasicPage, InstallationGuide


def named_page(document_name, *annotation_list):
    class NamedPage(PageType):
        annotations = PageType.annotations + list(annotation_list)

        def match(self, document):
            return document.name == document_name

    return NamedPage


bundle = Bundle(
    InstallationGuide,
    named_page('basicpage/longsections', LongSection))
