from signal import signal, SIGPIPE, SIG_DFL
import sys

from logbook import NullHandler, StreamHandler
import click

from .project import get_project
from .main import annotate


@click.command()
@click.argument('project')
@click.option('-r', '--recreate/--no-recreate', is_flag=True, help='Recreate all cached files.')
@click.option('--rdf', is_flag=True, help='Show RDF of doctree files and exit.')
@click.option('--debug/--no-debug', is_flag=True, help='Show debug output.')
@click.option('--tmp-dir', type=click.Path(), default='/tmp/annotatedocs', help='Set working directory in which the projects shall be downloaded.')
def main(project, recreate, rdf, debug, tmp_dir):

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
            project = get_project(project, base_dir=tmp_dir)
            if recreate:
                project.cleanup()
            project.setup()
            if rdf:
                annotate(project)
            project.build()
