HOST_PYTHON=$(shell which python3)
VENV=.venv
TESTS=tests/tests.py
REQS=requirements.txt
PYTHON=$(VENV)/bin/python
OK_TESTS=.ok_tests
OK_VENV=.ok_venv
OK_REQ=.ok_req
SRCS=$(shell find . -name '*.py')

all: $(OK_TESTS)

$(OK_VENV):
	$(HOST_PYTHON) -m venv .venv && touch $@

$(OK_REQ): $(OK_VENV) $(REQS)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r $(REQS) && touch $@

$(OK_TESTS): $(SRCS) $(TESTS) $(OK_REQ)
	$(PYTHON) -m unittest $(TESTS) && touch $@

clean:
	rm -f $(OK_TESTS) $(OK_VENV) $(OK_REQ)
	rm -rf $(VENV) dist build pynetstring.egg-info pynetstring-*.tar.gz __pycache__

dist: $(OK_TESTS) setup.py $(SRCS)
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel
	$(PYTHON) -m twine check dist/*

upload: dist
	$(PYTHON) -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*

timeit: all
	$(PYTHON) -m timeit -n 1000 -r 100 -s 'import pynetstring' 'pynetstring.decode(b"0:,0:,0:,3:abc,10:0123456789,52:abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,")'