TESTS=tests/tests.py
OK_TESTS=.ok_tests

all: $(OK_TESTS)

$(OK_TESTS): pynetstring.py $(TESTS)
	python3 -m unittest $(TESTS) && touch $@

clean:
	rm -f $(OK_TESTS)
	rm -rf dist build pynetstring.egg-info pynetstring-*.tar.gz

dist: $(OK_TESTS) setup.py pynetstring.py
	python3 setup.py sdist
	python3 setup.py bdist_wheel
