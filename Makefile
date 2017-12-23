TESTS=tests/tests.py
OK_TESTS=.ok_tests

all: $(OK_TESTS)

$(OK_TESTS): pynetstring.py $(TESTS)
	python3 -m unittest $(TESTS) && touch $@

clean:
	rm -f $(OK_TESTS)

dist: test setup.py pynetstring.py
	python3 -m setup.py
