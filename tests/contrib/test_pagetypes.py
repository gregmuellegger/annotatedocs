from annotatedocs.contrib.pagetypes.contribution_guide import ContributionGuide
from annotatedocs.contrib.pagetypes.installation_guide import InstallationGuide
from . import named_document as d


class TestInstallationGuide(object):
    def test_filename_matches(self):
        pagetype = InstallationGuide()

        assert pagetype.match(d('installing')) > 0
        assert pagetype.match(d('installation')) > 0
        assert pagetype.match(d('installation_guide')) > 0
        assert pagetype.match(d('intro/installation_guide')) > 0
        assert pagetype.match(d('installing_this_fancy_software')) > 0

        assert pagetype.match(d('index')) == 0
        assert pagetype.match(d('installer')) == 0
        assert pagetype.match(d('installed')) == 0


class TestContributionGuide(object):
    def test_filename_matches(self):
        pagetype = ContributionGuide()

        assert pagetype.match(d('contributing')) > 0
        assert pagetype.match(d('contribute')) > 0
        assert pagetype.match(d('howto/contribute')) > 0

        assert pagetype.match(d('contrib')) == 0
        assert pagetype.match(d('conterfite')) == 0
        assert pagetype.match(d('contributing/index')) == 0
        assert pagetype.match(d('contributors')) == 0
        assert pagetype.match(d('contributers')) == 0
        assert pagetype.match(d('contributed')) == 0
