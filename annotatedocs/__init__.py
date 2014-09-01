from annotatedocs.bundle import Bundle
from annotatedocs.checks import Check
from annotatedocs.metrics import Metric
from annotatedocs.page_types import PageType
from annotatedocs.annotations import Annotation, Hint, Warning


__version__ = '0.1.0'


def setup(app):
    app.add_config_value('annotatedocs_bundle',
                         'annotatedocs.bundles.default_bundle',
                         'annotatedhtml')
