Running locally
###############

Using `docker compose` (recommended)
====================================

Build docker images:

.. code:: shell

    ./bin/dev/build

Start the services:

.. code:: shell

    ./bin/dev/start

.. note::

    The ``docker compose`` configuration contains directives to
    automatically update changed code inside the container, and to
    completely rebuild the container in case dependencies in
    ``uv.lock`` are changed.

    In some cases, manually building and restarting might still be
    required.

Create database schema (only needed once):

.. code:: shell

    ./bin/dev/cli db create-schema


Accessing the application
-------------------------

- The main application can be accessed at http://localhost:8000/
- The web API is exposed at http://localhost:8001/ (`docs <http://localhost:8001/docs>`_)
- To connect to the database, use ``./bin/dev/psql`` (or ``docker compose exec db psql``).
- Emails sent by the app will be visible at http://localhost:8026/


Linting & formatting
====================

To check linting rules:

.. code:: shell

    ./bin/dev/style-check

To automatically fix:

.. code:: shell

    ./bin/dev/style-fix
