# New MoWAKi Project

Application created with [MoWAKi].

[MoWAKi]: https://github.com/rshk/mowaki-project


## Installing

Install backend dependencies:

    pipenv install


Install frontend dependencies:

    cd web && yarn install


Run database migrations:

    pipenv run alembic upgrade head


## Configuring

Create an ``.env`` file containing the necessary configuration:

```
PYTHONPATH=.
SECRET_KEY=notasecret
DATABASE_URL=postgres://postgres:@localhost:5432/default
REDIS_URL=redis://localhost:6379
```


## Running

Start the necessary services via docker-compose:

    docker-compose up


Start the backend server:

    pipenv run start


Start the frontend server:

    cd web && yarn start


Then head to http://localhost:8000/

You can also access GraphiQL running at http://localhost:5000/graphql
