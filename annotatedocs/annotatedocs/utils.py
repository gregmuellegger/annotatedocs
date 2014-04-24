import os


class cd(object):
    """
    Context manager for changing the current working directory

    Inspired by: http://stackoverflow.com/a/13197763/199848
    """

    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
