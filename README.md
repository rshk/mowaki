# Mowaki 2.0

Modular Web Application Kit

## Architecture

![MoWaKi Architecture](https://raw.githubusercontent.com/rshk/mowaki/mowaki-2.0/.files/MoWaKi%20Architecture.png)


## Project scaffolding

### The ``app`` folder

Contains the main runtime code for the backend application.

#### Package: ``app.framework``

Framework-level utilities. Most of this can probably be moved to a 3rd-party package.

Modules in here can be imported from anywhere in the codebase.


#### Package: ``app.lib``

Misc libraries. Can be used by the whole codebase. Most of this code could reside in 3rd party packages.

Depends on: ``app.framework``.


#### Package: ``app.root``

"Root" utilities for the app. For example, configuration and resource context management.


#### Package: ``app.models``

(Or types?) Definition of the base types used in the app. Can be used by the whole codebase.

Depends on: ``app.framework``, ``app.lib``.


#### Package: ``app.io``

Low-level resource access utilities. Examples: database connections, 3rd party API clients.

Depends on: ``app.framework``, ``app.lib``, ``app.models``.


#### Package: ``app.repo``

Repo functions. Provide an abstraction over the lower level resources.

Depends on: ``app.io`` (and ``app.framework``, ``app.lib``, ``app.models``).


#### Package: ``app.core``

Core business logic.

Depends on: ``app.repo``, ``app.framework``, ``app.lib``, ``app.models``.

Shouldn't access ``app.io`` directly unless it really makes sense to
do so (eg. accessing a 3rd party library with no need for any layer in
between).


#### Package: ``app.webapi``

Web API interface.

Depends on: ``app.core``, ``app.framework``, ``app.lib``, ``app.models``.


#### Package: ``app.cli``

Command line interface.

Depends on: ``app.core``, ``app.framework``, ``app.lib``, ``app.models``.


### The ``tests`` folder

Contains tests for the backend app.

#### Module: ``tests.conftest``

Configuration for ``pytest``. Mainly loads fixtures from ``tests.fixtures``

#### Package: ``tests.fixtures``

Fixture functions for the tests. Includes a ``factory`` fixture to access factories.

#### Package: ``tests.factories``

Factories for database objects, if it makes sense for the project.


### The ``web`` folder

Contains the web frontend code.

TODO (which frontend should we use btw? Probably React but what framework?)


## Configuration files


## Build and run configuration (prod, testing, dev)

- Docker and docker-compose
- Utilities from the ``bin`` folder
