init:
	pip install -r requirements.txt

test:
	pytest

dist:
	python setup.py sdist && python setup.py bdist_wheel

publish:
	twine upload dist/*

changelog:
	github_changelog_generator
