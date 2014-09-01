from annotatedocs import Bundle, NamedPage

from annotatedocs.contrib.checks.has_no_long_sections import HasNoLongSections
from annotatedocs.contrib.checks.no_passive_voice_used import NoPassiveVoiceUsed
from annotatedocs.contrib.checks.is_pep8_compliant import IsPEP8Compliant
from annotatedocs.contrib.pagetypes.homepage import Homepage
from annotatedocs.contrib.pagetypes.installation_guide import InstallationGuide


def page_type_for_path(path, page_type_class):
    return type(page_type_class.__name__, (page_type_class,), {
        'match': lambda self, document: int(document.name.startswith(path))
    })


bundle = Bundle(
    InstallationGuide,
    NamedPage('basicpage/longsections', [HasNoLongSections]),
    NamedPage('basicpage/passivevoice', [NoPassiveVoiceUsed]),
    NamedPage('basicpage/pep8compliance', [IsPEP8Compliant]),
    page_type_for_path('pagetypes/homepage/', Homepage))
