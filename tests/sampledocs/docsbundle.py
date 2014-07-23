from annotatedocs.bundle import Bundle
from annotatedocs.page_types import PageType, BasicPage, InstallationGuide


class LongSectionPage(PageType):
    def match(self, document):
        return document.name == 'basicpage/longsections'


bundle = Bundle(
    InstallationGuide,
    LongSectionPage)
