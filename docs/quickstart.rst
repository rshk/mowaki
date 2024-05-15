Quick Start
###########

Clone the repo::

    git clone https://github.com/rshk/mowaki.git my-project-name

Create a base commit::

    cd my-project-name
    MOWAKI_COMMIT_ID="$( git rev-parse HEAD )"
    rm -rf .git
    git init
    git add .
    git commit -m "MoWAKi ${MOWAKI_COMMIT_ID}"

Create a configuration file (``.env``)::

    ./bin/create-env-file

Start the services::

    docker compose up

Run the test suite::

    ./bin/docker/pytest -vvv ./tests

Run GraphQL queries using GraphiQL at http://localhost:8080/.

Example GraphQL query:


.. code:: graphql

    {
      hello(name:"World")
    }
