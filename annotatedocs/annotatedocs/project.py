import os

from logbook import Logger
from .builder import AnnotatedSphinx
from .utils import tempdir


log = Logger(__name__)


class Project(object):
    def __init__(self, loader):
        self.loader = loader

    def setup(self):
        '''
        Prepare all the steps that are needed before we can attempt a build.
        '''

        self.loader.setup()

    def cleanup(self):
        '''
        Delete all cached files that are needed to build the annotated docs.
        '''

        self.loader.cleanup()

    def build(self):
        with tempdir() as doctrees_dir:
            app = AnnotatedSphinx(
                srcdir=unicode(self.loader.get_docs_dir()),
                confdir=unicode(self.loader.get_docs_dir()),
                outdir=unicode(self.loader.get_build_dir()),
                doctreedir=unicode(doctrees_dir),
                buildername='html')
            app.build(force_all=True)
            index_file = os.path.join(
                self.loader.get_build_dir(),
                'index.html')
            log.info(
                'Build finished. Open file://{path} in your browser to see '
                'the annotations.'.format(path=index_file))
            return index_file
