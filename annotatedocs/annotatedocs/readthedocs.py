import os

from logbook import Logger
import sh
import slumber

from .utils import cd


log = Logger(__name__)


api = slumber.API(base_url='http://readthedocs.org/api/v1/')


class Project(object):
    dependencies = ['Sphinx']

    def __init__(self, slug, repository, file_suffix, install_python_package, pip_requirements_file):
        self.slug = slug
        self.repository_url = repository
        self.file_suffix = file_suffix
        self.install_python_package = install_python_package
        self.pip_requirements_file = pip_requirements_file

        self.repository_dir = '/tmp/annotatedocs/{}/repo'.format(slug)
        self.virtualenv_dir = '/tmp/annotatedocs/{}/venv'.format(slug)

    def checkout_repository(self):
        log.info('Checking out {} -> {}'.format(
            self.repository_url,
            self.repository_dir))
        if not os.path.exists(self.repository_dir):
            os.makedirs(self.repository_dir)
        sh.git.clone(self.repository_url, self.repository_dir)

    def update_repository(self):
        log.info('Updating repository in {}'.format(self.repository_dir))
        with cd(self.repository_dir):
            output = sh.git.pull()
            log.debug('git pull: {}'.format(output))

    def setup_repository(self):
        if not os.path.exists(os.path.join(self.repository_dir, '.git')):
            self.checkout_repository()
        else:
            log.debug('Directory already exists, assuming it contains the right checkout: {}'.format(self.repository_dir))
            self.update_repository()

    def get_virtualenv_command(self, executable):
        return sh.Command(os.path.join(self.virtualenv_dir, 'bin', executable))

    def setup_virtualenv(self):
        log.info('Setting up virtualenv in {}'.format(self.virtualenv_dir))
        if not os.path.exists(self.virtualenv_dir):
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

    def build_doctrees(self):
        pass

    def setup(self):
        '''
        Prepare all the steps that are needed before we can attempt a build.
        '''

        self.setup_repository()
        self.setup_virtualenv()

    def build(self):
        pass


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
