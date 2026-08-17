Running tests
#############

Using `docker compose` (recommended)
====================================

To run the Python tests in a temporary container:

.. code:: shell

    docker compose run --rm api uv run pytest -vvv

.. important::

   Using `docker compose run` will run tests on the code contained in
   the latest *built* container image. Changes that were applied by
   `compose watch` will not be effective.

   If you want to run the test suite without rebuilding the container,
   use `docker compose exec` instead to run inside a runnig container
   (which will have the modified code in place):

   .. code:: shell

        docker compose exec api uv run pytest -vvv
