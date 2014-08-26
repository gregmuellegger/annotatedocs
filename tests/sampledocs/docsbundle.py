from annotatedocs.bundle import Bundle
from annotatedocs.checks import LongSection, PassiveVoice
from annotatedocs.checks.pep8 import PEP8Compliance
from annotatedocs.page_types import NamedPage, InstallationGuide
from annotatedocs.page_types.homepage import Homepage


def page_type_for_path(path, page_type_class):
    return type(page_type_class.__name__, (page_type_class,), {
        'match': lambda self, document: int(document.name.startswith(path))
    })


bundle = Bundle(
    InstallationGuide,
    NamedPage('basicpage/longsections', [LongSection]),
    NamedPage('basicpage/passivevoice', [PassiveVoice]),
    NamedPage('basicpage/pep8compliance', [PEP8Compliance]),
    page_type_for_path('pagetypes/homepage/', Homepage))
