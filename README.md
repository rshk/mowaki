# Mowaki 2.0

Modular Web Application Kit

## Architecture

![MoWaKi Architecture](https://raw.githubusercontent.com/rshk/mowaki/mowaki-2.0/.files/MoWaKi%20Architecture.png)


### The configuration layer

The configuration layer (defined in `app.config`) is used to retrieve
(and validate) configuration from environment variables, and make it
available to the rest of the code using a `ContextVar`.

- Public interface: `self`


### The resources layer

The resources layer (defined in `app.resources`) is responsible for
instantiating clients to all the external services being used.

This includes:

- databases
- message queues
- smtp providers
- 3rd party web APIs

Note that these clients will generally *not* be accessed directly by
the business logic, but instead they'll be used through the Repo and /
or IO layers described below.

- Depends on: `configuration`
- Public interface: `self`


### The repo layer

The repo layer (`app.repo.*`) provides abstraction over permanent storage,
eg. databases and file storage, considered "internal" to the
application.

Sub-modules and the root level of sub-packages are considered public
interface, unless their name starts with an underscore (`_`).

- Depends on: `resources`, `models`, `config`
- Used by: `core`
- Public interface: `submodules`


### The I/O layer

The I/O layer (`app.io.*`) provides abstraction over access to
3rd-party services, eg. SMTP servers or Web APIs.

Sub-modules and the root level of sub-packages are considered public
interface, unless their name starts with an underscore (`_`).

- Depends on: `resources`, `models`, `config`
- Used by: `core`
- Public interface: `submodules`


### The Core layer

The Core layer (`app.core.*`) contains the actual business logic of the application.

It can be structured in any way that fits the domain, and provides the
main library interface into the application, which upper layers can
use to expose functionality through a number of interfaces.

- Depends on: `repo`, `io`, `models`, `config`
- Used by: interface layers (`webapp`, `cli`, ...)
- Public interface: `tree` (or anything that makes sense for the
  particular application)


### The Web API layer

Provides a Web API interface (GraphQL, but RESTful can also be used,
or any other type of web API format, even at the same time) into the
application business logic.


### The command-line interface

Typically used for administrative commands (eg. creating the first
admin user on a production server).

Core functions are typically invoked as a special "superuser", which
is not tied to an actual user in the database, and provide extra
privileges not normally accessible to the web application users.


### Async workers

Async workers are typically separate processes that listen for
messages or events on some type of queue, and execute tasks
accordingly.

Worker processes can be create wherever it makes sense (eg. in an
`app.workers` package), and extra services can be added to the
`docker-compose.yml` file to start the processes.


### Models

The models package `app.models` contains all the domain objects
(usually data structures defined using the `dataclasses` module) that
are used to represent data inside the application.

- Used by: `core`, `repo`, `io`
- Public interface: `tree`


### Library code

The `app.lib` package can contain any generic code that is not
strictly part of the business logic.

A good rule of thumb is that code inside this package could be
eventually split into a completely separate library.

- Can be used (sensibly) by any part of the codebase
- Depends on: no other part of the codebase a part from within `app.lib` itself
- Public interface: any


### Definition: public interface

- `self`: any public object defined in the module itself, or in the
  top-level `__init__.py` for packages.

- `submodules`: public objects defined in first-level modules or
  packages with a name not starting with `_` are considered public.

- `tree`: any public objects contained in any sub-module or
  sub-package not starting with `_` are considered public.









## Build and run configuration (prod, testing, dev)

- Docker and docker-compose
- Utilities from the ``bin`` folder







## Development

### Installation


### Configuration


### Database migrations


### Running a development server

The development setup relies on a `.env` file to pass environment
variables to the application via `docker compose`.


## Testing


### Running the test suite


### Writing tests


## Debugging


## Integrating a front-end


## Production

### Installation


### Configuration


### Database migrations


### Running a production server
