import logging

from app.config import load_config
from app.resources import initialize_resources

from .app import create_app

# Setup logging ------------------------------------------------------

# TODO: consider switching to something more modern, like logbook
# https://logbook.readthedocs.io/en/stable/

logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.addHandler(logging_handler)
root_logger.setLevel(logging.INFO)

app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)


# Initialize configuration and resources -----------------------------

config = load_config()
resources = initialize_resources(config, set_context=True)


# Create FastAPI app -------------------------------------------------

app = create_app()
