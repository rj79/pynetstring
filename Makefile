TESTS=tests/tests.py
OK_TESTS=.ok_tests
SRCS=$(shell find . -name '*.py')
all: $(OK_TESTS)

$(OK_TESTS): $(SRCS) $(TESTS)
	python3 -m unittest $(TESTS) && touch $@

clean:
	rm -f $(OK_TESTS)
	rm -rf dist build pynetstring.egg-info pynetstring-*.tar.gz __pycache__

dist: $(OK_TESTS) setup.py $(SRCS)
	python3 setup.py sdist
	python3 setup.py bdist_wheel
