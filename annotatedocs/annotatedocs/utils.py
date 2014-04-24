import os


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
