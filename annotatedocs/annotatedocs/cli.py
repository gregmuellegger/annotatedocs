import sys

from logbook import NullHandler, StreamHandler
import click

from .readthedocs import get_project


@click.command(pass_context=True)
@click.argument('project', help='A read the docs project name.')
@click.option('-r', '--recreate/--no-recreate', default=False, help='Recreate all cached files.')
@click.option('-d', '--debug/--no-debug', default=False, help='Show debug output.')
def main(ctx, project, recreate=False, debug=False):
    if debug:
        log_level = 'DEBUG'
    else:
        log_level = 'INFO'

    null_handler = NullHandler(level='DEBUG')
    log_handler = StreamHandler(sys.stderr, level=log_level)
    with null_handler.applicationbound():
        with log_handler.applicationbound():
            project = get_project(project)
            if recreate:
                project.cleanup()
            project.setup()
