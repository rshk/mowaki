Running locally
###############

Using `docker compose` (recommended)
====================================

Build docker images:

.. code:: shell

    docker compose build

Start the services:

.. code:: shell

    docker compose up --watch

This should automatically restart the service upon changes, and
rebuild the images upon changes to `uv.lock`. Manual restarting might
still be required in some cases.
