import click
from .readthedocs import get_project


@click.command()
@click.argument('project', help='A read the docs project name.')
def main(project):
    project = get_project(project)
    project.setup()
