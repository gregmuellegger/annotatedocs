import tempfile
import os
import shutil


class cd(object):
    """
    Context manager for changing the current working directory

    Inspired by: http://stackoverflow.com/a/13197763/199848
    """

    def __init__(self, new_path):
        self.new_path = new_path

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


class tempdir(object):
    """
    Context manager for changing the current working directory

    Inspired by: http://stackoverflow.com/a/13197763/199848
    """

    def __enter__(self):
        self.temp_path = tempfile.mkdtemp()
        return self.temp_path

    def __exit__(self, etype, value, traceback):
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
