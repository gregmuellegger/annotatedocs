import os
import shutil
import traceback

from click.testing import CliRunner

from annotatedocs.cli import main


def get_sampledocs_dir():
    test_dir = os.path.dirname(
        os.path.abspath(__file__))
    return os.path.join(test_dir, 'sampledocs')


class AnnotatedocsCliRunner(CliRunner):
    def prepare_docs(self):
        cwd = os.getcwd()
        tmp_sampledocs_dir = os.path.join(cwd, 'sampledocs')
        shutil.copytree(get_sampledocs_dir(), tmp_sampledocs_dir)
        return {
            'root': tmp_sampledocs_dir,
        }


def test_build_of_sampledocs():
    runner = AnnotatedocsCliRunner()
    with runner.isolated_filesystem():
        docs = runner.prepare_docs()
        result = runner.invoke(main, [
            docs['root']
        ])

        if result.exit_code != 0:
            lines = traceback.format_exception(*result.exc_info)
            assert result.exit_code == 0, ''.join(lines)
