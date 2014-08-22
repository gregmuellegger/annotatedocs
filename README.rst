annotatedocs
============

``annotatedocs`` is a command line tool to analyze and annotate your docs with
useful information about it's quality. Use it to find common flaws in your
project's documentation and get tips on how to improve it.

.. note::
    The package is still in its infancy. So it propably does not fill any
    real need so far. However the basic framework is there for you to start
    building your own checks you can run against your own documentation
    project.

    Documentation on how to utilize it will follow soon.

Usage
-----

First install it with ``pip``::

    pip install "https://github.com/gregmuellegger/annotatedocs/archive/master.zip#egg=annotatedocs"

Then call the ``annotatedocs`` command with the path to your documentation
directory::

    annotatedocs project/docs/

This will generate a HTML build and will visualize the found annotations in the
HTML. Therefore call the URL that is displayed at the end of the build in your
browser to view the documentation and have a look at the added annotations.

.. note::
    ``annoatedocs`` can only operate on sphinx based documentation so far.

Todos
-----

The roadmap includes adding a few more features, which are:

* Add an output format option to the command line tool to get an output in JSON
  for easier further processing.
* Support and testing for more Python versions (mainly Python 3).
