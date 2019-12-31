# Your new MoWAKi Project

Application created with [MoWAKi].

Refer to [the official documentation] on how to get started making changes.

[MoWAKi]: https://github.com/rshk/mowaki-project
[the official documentation]: https://docs.mowaki.org/en/latest/


## Running (development mode)

Create a ``.env`` file, containing the required configuration:

    SECRET_KEY=write_something_random_here


Several docker-compose services are defined, for running the API / web
development servers, as well as some services (PostgreSQL and Redis).

To build the API server image:

    docker-compose build api

Nodejs dependencies are installed in a separate volume, so the local
node_modules directory can be shadowed by mounting it on top.

This means you need to run this to install / update changed dependencies:

    docker-compose run --entrypoint='' --rm --no-deps web npm install

Finally, to start the containers:

    docker-compose up

Then, head to http://localhost:8000 to see your newly created app.

You can also access GraphiQL, running on the API server at http://localhost:5000/graphql


### Running database migrations

To run database migrations:

    docker-compose run --entrypoint='' --rm api alembic upgrade head


### Customizing ports

By default, the web server will listen on ``localhost:8000``, while
the API server will listen on ``localhost:5000``.

This of course would prevent multiple MoWAKi apps from running on the
same host at once.

To work around that, you can use the ``WEB_PORT`` and ``API_PORT``
environment variables to change which local ports will be bound to the
containers. For example:

    WEB_PORT=8080 API_PORT=5555 docker-compose up


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


## Running (development mode, outside docker)

You can run the application without using Docker, if you prefer doing so.

Make sure you have any required service running locally (or you can
use the ones provided in the docker-compose configuration, just make
sure you map any required port).

Also, make sure the locally installed versions of Python and Node are
supported.

Create a configuration file (``.env``):

```
PYTHONPATH=.
SECRET_KEY=notasecret
DATABASE_URL=postgres://postgres:@localhost:5432/default
REDIS_URL=redis://localhost:6379
```

Install backend dependencies:

    pipenv install

Install frontend dependencies:

    cd web && npm install

Run database migrations:

    pipenv run alembic upgrade head

Start API server:

    pipenv run start

Start Web server:

    cd web && npm run start
