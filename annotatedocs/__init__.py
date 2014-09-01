from annotatedocs.bundles import *
from annotatedocs.checks import *
from annotatedocs.metrics import *
from annotatedocs.pagetypes import *
from annotatedocs.annotations import *


__version__ = '0.1.0'


def setup(app):
    app.add_config_value('annotatedocs_bundle',
                         'annotatedocs.bundles.default_bundle',
                         'annotatedhtml')
