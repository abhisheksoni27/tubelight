PYTHON=python3
PACKAGE=tubelight
PYPROJECT=pyproject.toml
SCRIPT_DIR=scripts

.PHONY: install clean build publish bump bump-patch bump-minor bump-major set-version

install:
	uv add -r requirements.txt

clean:
	rm -rf build dist *.egg-info __pycache__
	find . -name "__pycache__" -type d -exec rm -rf {} +

build: clean
	uv add build
	uv run $(PYTHON) -m build

publish: build
	uv add twine
	uv run $(PYTHON) -m twine upload dist/*

bump:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py $(TYPE)

bump-patch:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py patch

bump-minor:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py minor
	git add .
	git commit -m "Bump minor version"
	git push

bump-major:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py major

set-version:
	$(PYTHON) $(SCRIPT_DIR)/bump_version.py set $(VERSION)
