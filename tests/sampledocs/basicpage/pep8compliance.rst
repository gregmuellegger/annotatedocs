PEP 8 compliance
=============================

Here comes some sample code that is totally not PEP8 compliant:

.. code-block:: python

    from library_with_long_name import stuff_with_even_longernames_than_what_the_library_has, even_importing_multiple_items

    class A(object):
        def __init__(self, a,
            b,
                c):
            pass


        def method(self):
            pass


But this one is:


.. code-block:: python

    class A(object):
        pass


One with warnings only (contains a tab after the ``if True``):


.. code-block:: python

    raise DummyError, "Message"


With errors and warnings.


.. code-block:: python

    spam( ham[1], `{eggs: 2}`)


And some code that shouldn't be parsed at all, because it's bash.


.. code-block:: bash

    if [ -e ~/.allyourbasebelongtous ]
        rm -rf *
    fi


And some code that is no valid python.


.. code-block:: python

    if : True
    except:

    if [ -e ~/.allyourbasebelongtous ]
        rm -rf *
    fi so wrong
