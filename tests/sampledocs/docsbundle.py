from annotatedocs import Bundle, NamedPage

from annotatedocs.contrib.checks.longsection import LongSection
from annotatedocs.contrib.checks.passivevoice import PassiveVoice
from annotatedocs.contrib.checks.pep8 import PEP8Compliance
from annotatedocs.contrib.pagetypes.homepage import Homepage
from annotatedocs.contrib.pagetypes.installation_guide import InstallationGuide


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
