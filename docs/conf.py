# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MoWAKi'
copyright = '2024, Sam Santi'
author = 'Sam Santi'
release = '2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_theme_options = {
    'logo': 'mowaki.png',
    'logo_name': True,
    'logo_text_align': 'center',

    'description': """
    <p style="text-align: center">
        <strong>Modern Web Application Kit.</strong><br/>
        Quickly build applications with Python, React and GraphQL.<br/>
    </p>
    <p>
        Homepage: <a href="https://mowaki.org">mowaki.org</a>.<br/>
        Repo: <a href="https://github.com/rshk/mowaki">rshk/mowaki</a>.<br/>
    </p>
    """,

    'github_user': 'rshk',
    'github_repo': 'mowaki',
    'github_button': True,
}

html_static_path = ['_static']
