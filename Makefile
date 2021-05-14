help:
	@echo " "
	@echo "Targets:"
	@echo " "
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
