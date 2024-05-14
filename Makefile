TARGETS = requirements.txt requirements-dev.txt

all: $(TARGETS)

requirements.txt: pyproject.toml
	poetry export --without-hashes > $@

requirements-dev.txt: pyproject.toml
	poetry export --without-hashes --with dev > $@

docs/requirements.txt: pyproject.toml
	poetry export --without-hashes --only=docs > $@

clean:
	rm -f $(TARGETS)
