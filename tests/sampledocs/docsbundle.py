from annotatedocs.bundle import Bundle
from annotatedocs.checks import LongSection, PassiveVoice
from annotatedocs.page_types import PageType, BasicPage, InstallationGuide


def named_page(document_name, *additional_checks):
    class NamedPage(PageType):
        checks = PageType.checks + list(additional_checks)

        def match(self, document):
            return document.name == document_name

    return NamedPage


bundle = Bundle(
    InstallationGuide,
    named_page('basicpage/longsections', LongSection),
    named_page('basicpage/passivevoice', PassiveVoice))
