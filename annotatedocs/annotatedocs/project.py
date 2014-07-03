import os
import pickle

from logbook import Logger
from rdflib import Graph, Namespace, Literal
import sh
import shutil
import slumber

from . import doctree2rdf
from . import reasoner
from .builder import AnnotatedSphinx
from .utils import cd


log = Logger(__name__)


api = slumber.API(base_url='http://readthedocs.org/api/v1/')


class Project(object):
    dependencies = ['Sphinx']

    def __init__(self, base_dir, slug, repository, file_suffix, install_python_package,
            pip_requirements_file):
        self.base_dir = base_dir
        self.slug = slug
        self.repository_url = repository
        self.file_suffix = file_suffix
        self.install_python_package = install_python_package
        self.pip_requirements_file = pip_requirements_file

        self.project_dir = os.path.join(self.base_dir, slug)
        self.repository_dir = os.path.join(self.project_dir, 'repo')
        self.virtualenv_dir = os.path.join(self.project_dir, 'venv')
        self.build_dir = os.path.join(self.project_dir, 'build')
        self.doctrees_dir = os.path.join(self.build_dir, 'doctrees')
        self.build_html_dir = os.path.join(self.build_dir, 'html')
        self.build_annotated_html_dir = os.path.join(self.build_dir, 'annotated')

    def setup_repository(self):
        exists = os.path.exists(self.repository_dir)
        if exists:
            log.debug('Using existing checkout: {}'.format(self.repository_dir))
            return

        log.info('Checking out {} -> {}'.format(
            self.repository_url,
            self.repository_dir))
        if not os.path.exists(self.repository_dir):
            os.makedirs(self.repository_dir)
        sh.git.clone(self.repository_url, self.repository_dir)

    def get_virtualenv_command(self, executable):
        return sh.Command(os.path.join(self.virtualenv_dir, 'bin', executable))

    def setup_virtualenv(self, recreate=False):
        exists = os.path.exists(self.virtualenv_dir)
        if not exists:
            log.info('Setting up virtualenv in {}'.format(self.virtualenv_dir))
            os.makedirs(self.virtualenv_dir)

            # Setup virtualenv.
            sh.virtualenv(self.virtualenv_dir)

            pip = self.get_virtualenv_command('pip')

            # Install Sphinx.
            for output in pip.install('--upgrade', *self.dependencies, _iter=True):
                log.debug('pip install: {}'.format(output))

            # Install python package if needed.
            if self.install_python_package:
                python = self.get_virtualenv_command('python')
                with cd(self.repository_dir):
                    log.info('Installing python package')
                    python('setup.py', 'install')

            # Install project's dependencies if there are any.
            if self.pip_requirements_file:
                requirements_file = os.path.join(
                    self.repository_dir,
                    self.pip_requirements_file)
                log.info('Installing python dependencies from {}'.format(requirements_file))
                pip.install(r=requirements_file)
        else:
            log.debug('Using existing virtualenv: {}'.format(self.virtualenv_dir))

    @property
    def docs_dir(self):
        if not hasattr(self, '_docs_dir'):
            possible_names = ['docs', 'doc']
            for name in possible_names:
                docs_dir = os.path.join(self.repository_dir, name)
                if os.path.exists(docs_dir):
                    self._docs_dir = docs_dir
                    break
            else:
                raise ValueError('No docs directory found in {0}'.format(self.repository_dir))
        return self._docs_dir

    def build_doctrees(self):
        exists = os.path.exists(self.doctrees_dir)
        if exists:
            log.debug('Using existing doctrees: {}'.format(self.doctrees_dir))
            return

        log.info('Building doctrees.')
        sphinx_build = self.get_virtualenv_command('sphinx-build')
        stdout = sphinx_build(
            '-b', 'html',
            '-d', self.doctrees_dir,
            self.docs_dir,
            self.build_html_dir,
            _iter=True)
        for line in stdout:
            log.debug('sphinx-build: {}'.format(line))

    def setup(self):
        '''
        Prepare all the steps that are needed before we can attempt a build.
        '''

        self.setup_repository()
        self.setup_virtualenv()
        self.build_doctrees()

    def cleanup(self):
        '''
        Delete all cached files that are needed to build the annotated docs.
        '''

        if os.path.exists(self.project_dir):
            log.info('Cleaning up (i.e. deleting) {}'.format(self.project_dir))
            shutil.rmtree(self.project_dir)

    def get_documents(self):
        exists = os.path.exists(self.doctrees_dir)
        if not exists:
            raise ValueError('Doctrees have not been built yet.')

        doctrees = []
        for path, dirs, files in os.walk(self.doctrees_dir):
            for file_path in files:
                doctree_path = os.path.join(path, file_path)
                if doctree_path.endswith('.doctree'):
                    with open(doctree_path, 'r') as f:
                        document_name = os.path.join(self.repository_url, file_path)
                        doctrees.append(
                            doctree2rdf.load(
                                f,
                                {'document_name': document_name}))
        return doctrees

    def get_graph(self, raw=False):
        graph = Graph()
        graph += doctree2rdf.get_ontology()
        for document in self.get_documents():
            graph += document.get_graph()
        return graph

    def build(self):
        app = AnnotatedSphinx(
            srcdir=self.docs_dir,
            confdir=self.docs_dir,
            outdir=self.build_annotated_html_dir,
            doctreedir=self.doctrees_dir,
            buildername='html')
        app.build(force_all=True)
        index_file = os.path.join(
            self.build_annotated_html_dir,
            'index.html')
        log.info(
            'Build finished. Open file://{path} in your browser to see the '
            'annotations.'.format(path=index_file)
        )


def get_project(slug, **kwargs):
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
