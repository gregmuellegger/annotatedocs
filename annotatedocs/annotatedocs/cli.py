import hashlib
from signal import signal, SIGPIPE, SIG_DFL
import sys

from logbook import NullHandler, StreamHandler
import click

from .loader import get_project_loader
from .project import Project


def get_token(string):
    return hashlib.sha1(string).hexdigest()


@click.command()
@click.argument('docs', type=click.Path(), default='.')
@click.option('-b', '--build-dir', type=click.Path(), default=None, help='Set build directory in which the annotated html shall be placed.')
@click.option('--tmp-dir', type=click.Path(), default=None, help='Set working directory in which the projects shall be downloaded.')
@click.option('-r', '--recreate/--no-recreate', is_flag=True, help='Recreate all cached files.')
@click.option('--debug/--no-debug', is_flag=True, help='Show debug output.')
def main(docs, build_dir, tmp_dir, recreate, debug):
    '''
    annotatedocs analyzes your sphinx-based documentation and provides helpful
    feedback about the quality and possible improvements.

    The first argument should be the path to where your documentation lives
    (e.g. the one in which you usually call 'make html').

    If you leave the first argument empty it defaults to the current working
    directory.

    The build will usually be written to <your docs dir>/_build/annotatedhtml/.
    You can change the output directory with the -b option.
    '''

    # Ignore SIG_PIPE so that piping works correctly.
    signal(SIGPIPE, SIG_DFL)

    if debug:
        log_level = 'DEBUG'
    else:
        log_level = 'INFO'

    null_handler = NullHandler(level='DEBUG')
    log_handler = StreamHandler(sys.stderr, level=log_level)
    with null_handler.applicationbound():
        with log_handler.applicationbound():

            loader = get_project_loader(docs,
                                        build_dir=build_dir,
                                        tmp_dir=tmp_dir)

            project = Project(loader)

            if recreate:
                project.cleanup()
            project.setup()
            project.build()
