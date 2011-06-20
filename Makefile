all: check_dependencies unit functional

filename=github-`python -c 'import github;print github.version'`.tar.gz

export GITHUB_DEPENDENCIES:= sure nose HTTPretty tornado simplejson httplib2

check_dependencies:
	@echo "Checking for dependencies to run tests ..."
	@for dependency in `echo $$GITHUB_DEPENDENCIES`; do \
		python -c "import $$dependency" 2>/dev/null || (echo "missing a dependency, please run pip install -Ur requirements.pip" && exit 3) ; \
		done

unit: clean
	@echo "Running unit tests ..."
	@nosetests -s --verbosity=2 --with-coverage --cover-erase --cover-inclusive tests/unit --cover-package=github

functional: clean
	@echo "Running functional tests ..."
	@nosetests -s --verbosity=2 --with-coverage --cover-erase --cover-inclusive tests/functional --cover-package=github

clean:
	@printf "Cleaning up files that are already in .gitignore... "
	@for pattern in `cat .gitignore`; do rm -rf $$pattern; done
	@echo "OK!"

release: clean unit functional
	@printf "Exporting to $(filename)... "
	@tar czf $(filename) github setup.py README.md COPYING
	@echo "DONE!"
