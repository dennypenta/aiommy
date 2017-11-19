.PHONY: deps test flake isort packaging release


deps:
	pip install -r requirements.requirements-all.txt

test:
	green -s 1 -f tests

flake:
	flake8 aiommy

isort:
	isort -rc aiommy
	isort -rc tests

packaging:
	python setup.py sdist
	python setup.py bdist_wheel
	twine upload dist/*

release: flake isort test packaging
