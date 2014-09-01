from ... import Bundle, PageType

from ..checks.passivevoice import NoPassiveVoiceUsed
from ..checks.is_pep8_compliant import IsPEP8Compliant
from ..pagetypes.homepage import Homepage
from ..pagetypes.contribution_guide import ContributionGuide
from ..pagetypes.installation_guide import InstallationGuide


class GenericPage(PageType):
    checks = [
        NoPassiveVoiceUsed,
        IsPEP8Compliant,
    ]

    def match(self, document):
        return 1


bundle = Bundle(
    Homepage,
    ContributionGuide,
    InstallationGuide,
    GenericPage)
