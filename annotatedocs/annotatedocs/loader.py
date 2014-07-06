import os
import re
import tempfile

from logbook import Logger
import sh
import shutil
import slumber

from .utils import cd


log = Logger(__name__)


def get_project_loader(path, **kwargs):
    for regex, loader_class in PREFIXED_LOADERS:
        match = re.match(regex, path)
        if match:
            kwargs.update(match.groupdict())
            return loader_class(**kwargs)

    # We assume it's a local directory.
    abs_path = os.path.abspath(path)
    return LocalLoader(path=abs_path, **kwargs)


class Loader(object):
    '''
    A loader class is reponsible for the following things:

        * Defining the tmp dir where temporary files can be placed, e.g. for
          the build.
        * Defining where the build shall be placed.
        * Initializes a virtualenv if required.
        * Cleaning up temporary files if requested.

    Subclasses can also take care of checking out a repository etc.
    '''

    conf_file = 'conf.py'
    dependencies = ['Sphinx']

    def __init__(self, path, build_dir=None, tmp_dir=None):
        self.path = path
        self.tmp_dir = self.find_tmp_dir(tmp_dir)
        self.build_dir = self.find_build_dir(build_dir)

    def get_default_tmp_dir(self):
        return tempfile.mkdtemp()

    def get_default_build_dir(self):
        return os.path.join(self.get_tmp_dir(), 'build')

    def find_tmp_dir(self, tmp_dir):
        '''
        Defines where the tmp_dir is placed. This should default to what is
        given with --tmp-dir during command invocation.
        '''
        if not tmp_dir:
            tmp_dir = self.get_default_tmp_dir()
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        return tmp_dir

    def find_build_dir(self, build_dir):
        '''
        Defines where the build is placed. This should default to what is
        given with --build-dir during command invocation.
        '''
        if not build_dir:
            build_dir = self.get_default_build_dir()
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        return build_dir

    def get_tmp_dir(self):
        return self.tmp_dir

    def get_build_dir(self):
        return self.build_dir

    def setup(self):
        self.doctrees_dir = os.path.join(self.get_tmp_dir(), 'doctrees')

        self.setup_project()
        self.setup_virtualenv()

    def setup_project(self):
        '''
        This is a hook that subclasses can use to checkout the given repository
        or to prepare the local path in other ways.
        '''
        pass

    def get_docs_dir(self):
        raise NotImplementedError('Needs to be implemented by subclass.')

    def get_doctrees_dir(self):
        return os.path.join(self.get_tmp_dir(), 'doctrees')

#    def check_for_conf(self):
#        if not os.path.exists(self.docs_path):
#            raise ValueError('TODO')
#
#        conf_filename = os.path.join(self.docs_path, self.conf_file)
#        if not os.path.exists(self.conf_filename):
#            raise ValueError('TODO')
#
#        pass

    def get_project_dir(self):
        '''
        Should return the base path to the project. If it's a python package it
        should also contain the ``setup.py`` file.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def get_virtualenv_dir(self):
        return os.path.join(self.get_tmp_dir(), 'venv')

    def get_virtualenv_command(self, executable):
        return sh.Command(os.path.join(self.get_virtualenv_dir(), 'bin', executable))

    def shall_install_python_package(self):
        return False

    def get_pip_requirements_file(self):
        raise NotImplementedError('Needs to be implemented by subclass.')

    def setup_virtualenv(self):
        virtualenv_dir = self.get_virtualenv_dir()
        exists = os.path.exists(virtualenv_dir)
        if not exists:
            log.info('Setting up virtualenv in {}'.format(virtualenv_dir))
            os.makedirs(virtualenv_dir)

            # Setup virtualenv.
            sh.virtualenv(virtualenv_dir)

            pip = self.get_virtualenv_command('pip')

            # Install Sphinx.
            for output in pip.install('--upgrade', *self.dependencies,
                                      _iter=True):
                log.debug('pip install: {}'.format(output))

            # Install python package if needed.
            if self.shall_install_python_package():
                python = self.get_virtualenv_command('python')
                with cd(self.get_project_dir()):
                    log.info('Installing python package')
                    python('setup.py', 'install')

            # Install project's dependencies if there are any.
            pip_requirements_file = self.get_pip_requirements_file()
            if pip_requirements_file:
                requirements_file = os.path.join(
                    self.get_project_dir(),
                    pip_requirements_file)
                log.info('Installing python dependencies from {}'.format(
                    requirements_file))
                pip.install(r=requirements_file)
        else:
            log.debug('Using existing virtualenv: {}'.format(
                virtualenv_dir))

    def cleanup(self):
        '''
        Delete all cached files that are needed to build the annotated docs.
        '''

        tmp_dir = self.get_tmp_dir()
        if os.path.exists(tmp_dir):
            log.info('Cleaning up (i.e. deleting) {}'.format(tmp_dir))
            shutil.rmtree(tmp_dir)


class LocalLoader(Loader):
    def get_default_build_dir(self):
        return os.path.join(self.get_docs_dir(), '_build', 'annotatedhtml')

    def get_docs_dir(self):
        return self.path

    def get_pip_requirements_file(self):
        return None


class VCSLoader(Loader):
    def __init__(self, path, *args, **kwargs):
        self.repository_url = path
        super(VCSLoader, self).__init__(path, *args, **kwargs)

    def get_repository_url(self):
        return self.repository_url

    def get_checkout_dir(self):
        return os.path.join(self.get_tmp_dir(), 'checkout')

    def get_project_dir(self):
        return self.get_checkout_dir()

    def get_docs_dir(self):
        '''
        Find the directory that contains the documentation.
        '''
        if not hasattr(self, '_docs_dir'):
            project_dir = self.get_project_dir()
            possible_names = ['docs', 'doc']
            for name in possible_names:
                docs_dir = os.path.join(project_dir, name)
                if os.path.exists(docs_dir):
                    self._docs_dir = docs_dir
                    break
            else:
                raise ValueError(
                    'No docs directory found in {0}'.format(project_dir))
        return self._docs_dir

    def setup_project(self):
        super(VCSLoader, self).setup_project()
        self.setup_repository()

    def setup_repository(self):
        checkout_dir = self.get_checkout_dir()
        exists = os.path.exists(checkout_dir)
        if exists:
            log.debug('Using existing checkout: {}'.format(checkout_dir))
            return

        log.info('Checking out {} -> {}'.format(
            self.get_repository_url(),
            checkout_dir))
        # Create parent directory of checkout.
        # The rest will be done by the VCS.
        parent_dir = os.path.dirname(checkout_dir)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        self.checkout_repository()


class GitLoader(VCSLoader):
    def __init__(self, path):
        raise NotImplementedError

    def checkout_repository(self):
        sh.git.clone(self.get_repository_url(), self.get_checkout_dir())


class SubversionLoader(VCSLoader):
    def __init__(self, path):
        raise NotImplementedError


class ReadTheDocsLoader(VCSLoader):
    api = slumber.API(base_url='http://readthedocs.org/api/v1/')

    def __init__(self, path, *args, **kwargs):
        self.project_name = path
        super(ReadTheDocsLoader, self).__init__(path, *args, **kwargs)

    def get_default_tmp_dir(self):
        return os.path.join('/tmp/annotatedocs', 'rtd', self.project_name)

    def get_repository_url(self):
        return self.project_data['repo']

    def setup(self):
        self.project_data = self.get_project_data(self.project_name)
        super(ReadTheDocsLoader, self).setup()

    def get_project_data(self, slug):
        data = self.api.project.get(slug=slug)
        assert data['meta']['total_count'] == 1, 'Project not found.'
        assert len(data['objects']) == 1
        project_data = data['objects'][0]
        assert project_data['repo_type'] == 'git', 'Only git repositories are supported.'
        return project_data

    def shall_install_python_package(self):
        return self.project_data['use_virtualenv']

    def get_pip_requirements_file(self):
        return self.project_data['requirements_file']

    def checkout_repository(self):
        sh.git.clone(self.get_repository_url(), self.get_checkout_dir())


PREFIXED_LOADERS = [
    (r'^git\+(?P<path>.+)$', GitLoader,),
    (r'^svn\+(?P<path>.+)$', SubversionLoader,),
    (r'^rtd\+(?P<path>[-a-zA-Z0-9]+)$', ReadTheDocsLoader,),
]