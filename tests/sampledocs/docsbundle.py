from annotatedocs.bundle import Bundle
from annotatedocs.checks import LongSection, PassiveVoice
from annotatedocs.checks.pep8 import PEP8Compliance
from annotatedocs.page_types import NamedPage, InstallationGuide


bundle = Bundle(
    InstallationGuide,
    NamedPage('basicpage/longsections', [LongSection]),
    NamedPage('basicpage/passivevoice', [PassiveVoice]),
    NamedPage('basicpage/pep8compliance', [PEP8Compliance]))
