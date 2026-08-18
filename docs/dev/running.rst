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

- Web app runs at `localhost:8000 <http://localhost:8000/>`_
- RESTful API runs at `localhost:8001 <http://localhost:8001/>`_ (`docs <http://localhost:8001/docs>`_)
- Sent emails can be seen at `localhost:8026 <http://localhost:8026/>`_
- Connect to postgres using ``./bin/dev/psql``


Linting & formatting
====================

To check linting rules:

.. code:: shell

    ./bin/dev/style-check

To automatically fix:

.. code:: shell

    ./bin/dev/style-fix
