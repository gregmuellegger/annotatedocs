import os

from logbook import Logger
from rdflib import Graph

from . import doctree2rdf
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

    def build_doctrees(self):
        doctrees_dir = self.loader.get_doctrees_dir()
        exists = os.path.exists(doctrees_dir)
        if exists:
            log.debug('Using existing doctrees: {}'.format(doctrees_dir))
            return doctrees_dir

        log.info('Building doctrees.')
        sphinx_build = self.loader.get_virtualenv_command('sphinx-build')
        with tempdir() as html_dir:
            stdout = sphinx_build(
                '-b', 'html',
                '-d', doctrees_dir,
                self.loader.get_docs_dir(),
                html_dir,
                _iter=True)
            for line in stdout:
                log.debug('sphinx-build: {}'.format(line))

        return doctrees_dir

    def build(self):
        doctrees_dir = self.build_doctrees()

        app = AnnotatedSphinx(
            srcdir=self.loader.get_docs_dir(),
            confdir=self.loader.get_docs_dir(),
            outdir=self.loader.get_build_dir(),
            doctreedir=doctrees_dir,
            buildername='html')
        app.build(force_all=True)
        index_file = os.path.join(
            self.loader.get_build_dir(),
            'index.html')
        log.info(
            'Build finished. Open file://{path} in your browser to see the '
            'annotations.'.format(path=index_file))


def get_project(slug, **kwargs):
    import slumber
    api = slumber.API(base_url='http://readthedocs.org/api/v1/')

    data = api.project.get(slug=slug)

    assert data['meta']['total_count'] == 1, 'Project not found.'
    assert len(data['objects']) == 1

    project_data = data['objects'][0]

    assert project_data['repo_type'] == 'git', 'Only git repositories are supported.'

    return Project(
        slug=project_data['slug'],
        repository=project_data['repo'],
        file_suffix=project_data['suffix'],
        install_python_package=project_data['use_virtualenv'],
        pip_requirements_file=project_data['requirements_file'],
        **kwargs)
