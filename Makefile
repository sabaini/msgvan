test: lint unittest functest

lint:
	tox -e lint

unittest:
	tox -e unittest

functest:
	tox -e functest

build: clean
	python -m pep517.build . 

pex: clean
	pex -o example/actorhandler.pex -D src -D example thespian attrs

clean: 
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -rf dist build .tox

# The targets below don't depend on a file
.PHONY: lint test unittest functest build clean




