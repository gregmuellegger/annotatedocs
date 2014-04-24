import os

from logbook import Logger
import sh
import shutil
import slumber

from .utils import cd


log = Logger(__name__)


api = slumber.API(base_url='http://readthedocs.org/api/v1/')


class Project(object):
    dependencies = ['Sphinx']

    def __init__(self, slug, repository, file_suffix, install_python_package,
            pip_requirements_file):
        self.slug = slug
        self.repository_url = repository
        self.file_suffix = file_suffix
        self.install_python_package = install_python_package
        self.pip_requirements_file = pip_requirements_file

        self.base_dir = os.path.join('/tmp', 'annotatedocs', slug)
        self.repository_dir = os.path.join(self.base_dir, 'repo')
        self.virtualenv_dir = os.path.join(self.base_dir, 'venv')
        self.docs_dir = os.path.join(self.repository_dir, 'docs')
        self.build_dir = os.path.join(self.base_dir, 'build')
        self.doctrees_dir = os.path.join(self.build_dir, 'doctrees')
        self.build_html_dir = os.path.join(self.build_dir, 'html')

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

        if os.path.exists(self.base_dir):
            log.info('Cleaning up (i.e. deleting) {}'.format(self.base_dir))
            shutil.rmtree(self.base_dir)


def get_project(slug):
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
    )
