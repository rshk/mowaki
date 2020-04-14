# Your new MoWAKi Project

Application created with [MoWAKi].

Refer to [the official documentation] on how to get started making changes.

[MoWAKi]: https://github.com/rshk/mowaki-project
[the official documentation]: https://docs.mowaki.org/en/latest/


## Setting up for development

Make sure you have a ``.env`` file with suitable configuration.

You can generate one by running:

```
./bin/create-env-file
```

Note that this is done automatically on new project initialization;
you have to run it manually if you cloned an existing project
repository.

Several docker-compose services are defined, for running the API / web
development servers, as well as some services (PostgreSQL and Redis).

Create a ``Pipfile.lock`` (required by the next step):

    pipenv lock

To build the API server image:

    docker-compose build api

Nodejs dependencies are installed in a separate volume, so the local
node_modules directory can be "shadowed" by mounting the volume on top.

This means you need to run this to install / update changed dependencies:

    docker-compose run --rm --no-deps web npm install

### Database

You might also want to set up your database schema, for running the demos.

    docker-compose run --rm api python -m app db create

See notes below about migrations, when you're ready to start development.


## Running (development mode)

Bring up the containers via docker-compose:

    docker-compose up

Then, head to http://localhost:8000 to see your newly created app.

You can also access GraphiQL, running on the API server at http://localhost:5000/graphql


### Using custom ports

By default, the web server will listen on ``localhost:8000``, while
the API server will listen on ``localhost:5000``.

This of course would prevent multiple MoWAKi apps from running on the
same host at once.

To work around that, you can use the ``WEB_PORT`` and ``API_PORT``
environment variables to change which local ports will be bound to the
containers. For example:

    WEB_PORT=8080 API_PORT=5555 docker-compose up


## Using the CLI

    docker-compose run --rm api python -m app


## Database management

A database schema can be created using the following commands:

    docker-compose run --rm api python -m app db create
    docker-compose run --rm api python -m app db drop

While that works, it is not recommended in production, as there is no
support for database migrations, allowing the schema to be changed.

A much better way would be to use database migrations via Alembic, as
illustrated below.

### Creating database migrations

    docker-compose run --rm --use-aliases api \
        alembic revision --autogenerate -m 'Your message here'


### Running database migrations

To run database migrations:

    docker-compose run --rm --use-aliases api \
        alembic upgrade head


## Development

### Installing Python dependencies

    pipenv install <name>
    docker-compose build api

Then restart docker-compose.


### Installing Nodejs dependencies

    cd web
    npm install <name>
    docker-compose run --rm --no-deps web npm install


### Connecting to database

To connect to the PostgreSQL database:

    docker-compose run --rm database bash -c 'psql "postgres://postgres:${POSTGRES_PASSWORD}@database:5432/default"'


### Connecting to a service directly

Sometimes you might want to, for example, connect to the database
server directly for inspecting something.

By default, container ports are not mapped to local ports, to reduce
the possible number of ports conflicts.

You can use this command to get the address of a local container:

    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mowaki_database_1

(user ``docker ps`` to list possible container names)

And connect to the database directly, eg:

    psql -U postgres -h 172.18.0.2


## Testing

Make sure you have a test database setup:

    docker-compose run --rm database bash -c 'psql "postgres://postgres:${POSTGRES_PASSWORD}@database:5432/default"'
    default=# CREATE DATABASE test_default;


To run tests:

    docker-compose run --rm -e TEST_MODE=1 api pytest -vvv ./tests
