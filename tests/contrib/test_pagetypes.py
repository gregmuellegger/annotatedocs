from annotatedocs.contrib.pagetypes.installation_guide import InstallationGuide


class InstallationGuideTests(object):
    def test_filename_matches(self):
        pagetype = InstallationGuide()

        assert pagetype.match('installing') > 0
        assert pagetype.match('installation') > 0
        assert pagetype.match('installation_guide') > 0
        assert pagetype.match('INSTALLATIONGUIDE') > 0
        assert pagetype.match('installing_this_fancy_software') > 0

        assert pagetype.match('index') == 0
        assert pagetype.match('installer') == 0
        assert pagetype.match('installed') == 0
