help:
	@echo " "
	@echo "Targets:"
	@echo " "
	@echo "- make run-unit-tests"
	@echo "- make check-quality"
	@echo "- make check-types"
	@echo "- make lint"
	@echo "- make check-format"
	@echo "- make format"
	@echo " "

check-quality:
		flake8 api/src/application/

check-types:
		# Check the types with mypy
		mypy api/src/application/

lint:
		pylint --rcfile .pylintrc api/src/application/

check-format:
		black api/src/application/ --check

format:
		black api/src/application/

run-unit-tests:

		pytest -v api/src/tests/application/unit_tests

run-integration-tests:

		pytest -v -p no:warnings api/src/tests/application/integration_tests

run-tests:

		pytest -v api/src/tests/application/unit_tests
		pytest -v -p no:warnings api/src/tests/application/integration_tests
