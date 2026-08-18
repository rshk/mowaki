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
