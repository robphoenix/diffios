init:
	pip install -r requirements.txt

test:
	pytest

changelog:
	github_changelog_generator
