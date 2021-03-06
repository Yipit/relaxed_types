# -*- coding: utf-8 -*-
PACKAGE=relaxed_types
TESTS_VERBOSITY=2
# </variables>

EXTRA_TEST_TASKS=

extra_args="$(filter-out $@,$(MAKECMDGOALS))"

%:
	@:

all: test

test: unit functional $(EXTRA_TEST_TASKS)

unit: setup
	@make run_test suite=unit pattern=$(extra_args)

functional: setup
	@make run_test suite=functional pattern=$(extra_args)

setup: clean
	@if [ -z $$VIRTUAL_ENV ]; then \
		echo "===================================================="; \
		echo "You're not running this from a virtualenv, wtf?"; \
		echo "ಠ_ಠ"; \
		echo "===================================================="; \
		exit 1; \
	fi
	@if [ -z $$SKIP_DEPS ]; then \
		echo "Installing dependencies..."; \
		pip install --quiet -r development.txt; \
	fi
	@pre-commit install


check_tests:
	@if [ -d tests/$(suite) ]; then \
		if [ `find tests/$(suite) -name 'test_*.py' | wc -l` -eq 0 ] ; then \
			echo "No \033[0;32m$(suite)\033[0m tests..."; \
		fi \
	else \
		echo "No \033[0;32mtest/$(suite)\033[0m directory found"; \
		exit 1; \
	fi
	$(eval HAS_SUITE = $(shell if [ -d tests/$(suite) ] && [ `find tests/$(suite) -name 'test_*.py' | wc -l` -ne 0 ]; then echo "yes"; else echo "no"; fi))


run_test: check_tests
	@if [ "$(HAS_SUITE)" == "yes" ]; then \
		echo "======================================="; \
		echo "* Running \033[0;32m$(suite)\033[0m test suite *"; \
		echo "======================================="; \
		py.test $(EXTRA_PYTEST) --cov-report term-missing --cov $(PACKAGE) -vv tests/$(suite); \
	fi
clean:
	@echo "Removing garbage..."
	@find . -name '*.pyc' -delete
	@rm -rf .coverage *.egg-info *.log build dist MANIFEST

tag:
	@if [ $$(git rev-list $$(git describe --abbrev=0 --tags)..HEAD --count) -gt 0 ]; then \
		if [ $$(git log  -n 1 --oneline $$(git describe --abbrev=0 --tags)..HEAD CHANGELOG.md | wc -l) -gt 0 ]; then \
			git tag $$(python setup.py --version) && git push --tags || echo 'Version already released, update your version!'; \
		else \
			echo "CHANGELOG not updated since last release!"; \
			exit 1; \
		fi; \
	else \
		echo "No commits since last release!"; \
		exit 1;\
	fi

publish: tag
	@if [ -e "$$HOME/.pypirc" ]; then \
		echo "Uploading to PyPI"; \
		python setup.py register -r pypi; \
		python setup.py sdist upload -r pypi; \
	else \
		echo "You should create a file called '.pypirc' under your home dir."; \
		echo "That's the right place to configure 'pypi' repos."; \
		exit 1; \
	fi
