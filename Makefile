TESTS=tests/tests.py
OK_TESTS=.ok_tests

all: $(OK_TESTS)

$(OK_TESTS): netstring_bin.py $(TESTS)
	python3 -m unittest $(TESTS) && touch $@

dist: test setup.py netstring.py
	python3 -m setup.py
