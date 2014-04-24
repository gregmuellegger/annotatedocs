import click
from .readthedocs import get_project


@click.command()
@click.argument('project', help='A read the docs project name.')
@click.option('-r', '--recreate/--no-recreate', default=False, help='Recreate all cached files.')
def main(project, recreate=False):
    project = get_project(project)
    if recreate:
        project.cleanup()
    project.setup()
