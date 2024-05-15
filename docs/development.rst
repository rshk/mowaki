Development
###########

Configuration is provided to start a development environment using ``docker compose``.


Local development
=================


Configuration
-------------

To create a ``.env`` configuration file::

    ./bin/create-env-file


Starting
--------

Run with docker compose::

    docker compose up


Testing
=======

Running the test suite
----------------------

Tests can be run inside a docker container:

    docker compose run --rm api pytest -vvv ./tests/

For convenience, the `./bin/docker/pytest` wrapper script can be used instead.


Writing tests
-------------

Tests are contained in the `tests` package.


Debugging
=========

TODO: add instructions on setting up a debugger
