from .app import create_app, setup_logging

setup_logging(debug=True)

app = create_app()

app.debug = True
