Building this documentation
###########################

Install dependencies:

.. code:: shell

    uv sync --group dev

To build locally:

.. code:: shell

    uv run make -C docs help

To rebuild automatically upon changes:

.. code:: shell

    uv run sphinx-autobuild docs docs/_build/html -b html
