PYTHON=python3
PACKAGE=tubelight
PYPROJECT=pyproject.toml
SCRIPT_DIR=scripts

.PHONY: install clean build publish bump bump-patch bump-minor bump-major set-version

install:
	$(PYTHON) -m pip install -r requirements.txt

clean:
	rm -rf build dist *.egg-info __pycache__
	find . -name "__pycache__" -type d -exec rm -rf {} +

build: clean
	uv run $(PYTHON) -m pip install --quiet build
	uv run $(PYTHON) -m build

publish: build
	uv run $(PYTHON) -m pip install --quiet twine
	uv run $(PYTHON) -m twine upload dist/*

bump:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py $(TYPE)

bump-patch:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py patch

bump-minor:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py minor

bump-major:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py major

set-version:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py set $(VERSION)
