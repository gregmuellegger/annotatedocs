from annotatedocs.bundle import Bundle
from annotatedocs.checks import LongSection, PassiveVoice
from annotatedocs.page_types import NamedPage, InstallationGuide


bundle = Bundle(
    InstallationGuide,
    NamedPage('basicpage/longsections', [LongSection]),
    NamedPage('basicpage/passivevoice', [PassiveVoice]))
