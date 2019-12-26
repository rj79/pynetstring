VENV=.venv
TESTS=tests/tests.py
REQS=requirements.txt
OK_TESTS=.ok_tests
OK_VENV=.ok_venv
OK_REQ=.ok_req
SRCS=$(shell find . -name '*.py')
all: $(OK_TESTS)

$(OK_VENV):
	python3 -m venv .venv && touch $@

$(OK_REQ): $(OK_VENV) $(REQS)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r $(REQS) && touch $@

$(OK_TESTS): $(SRCS) $(TESTS) $(OK_REQ)
	python3 -m unittest $(TESTS) && touch $@

clean:
	rm -f $(OK_TESTS) $(OK_VENV) $(OK_REQ)
	rm -rf $(VENV) dist build pynetstring.egg-info pynetstring-*.tar.gz __pycache__

dist: $(OK_TESTS) setup.py $(SRCS)
	python3 setup.py sdist
	python3 setup.py bdist_wheel
