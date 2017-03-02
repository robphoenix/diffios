.PHONY: docs

init:
	pip install -r requirements.txt

test:
	pytest

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"

changelog:
	github_changelog_generator
