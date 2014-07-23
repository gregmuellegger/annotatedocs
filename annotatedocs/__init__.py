__version__ = '0.1.0'


def setup(app):
    app.add_config_value('annotatedocs_bundle',
                         'annotatedocs.bundles.default_bundle',
                         'annotatedhtml')
