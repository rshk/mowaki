# Application folder

This application contains the main code of the application.


## Configuration

The ``app.config`` module contains a definition of the configuration
this app accepts from the environment.

Provides a ContextVar to access the app configuration.


## Library functions

The ``app.lib`` package contains various library-type functions that
are specific to the application.

Any of the other packages can depend on library functions.


## Models

Domain objects, used by the application business logic and the repo methods.


## Resources

Depends on: `config`, `lib`.

The ``app.resources`` module contains code to initialize various
"resources" (clients to 3rd party apps) used by this application.

Examples include databases, smtp service, API clients, ...

Used by the `repo` and `io` packages to access the actual underlying
resources.


## Repo

Persistence layer abstraction.

Depends on: `resources`, `models`, `config`

Database schema is defined in `app.repo._schema`. Other non-public
utilities used by the repo should be in `_*` modules or packages.


## I/O

Communication with 3rd party services.

Depends on: `resources`, `models`, `config`.


## Core

Depends on: `repo`, `io`, `models`, `lib`, `config`.

Main business logic.


## WebAPI

Depends on: `core`, `lib`, `config`

Web API (GraphQL) interface to the business logic.


## CLI

Depends on: `core`, `lib`, `config`

Command-line interface to the business logic.
