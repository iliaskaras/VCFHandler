help:
	@echo " "
	@echo "Targets:"
	@echo " "
	@echo "- make run-tests"
	@echo "- make run-unit-tests"
	@echo "- make run-integration-tests"
	@echo "- make deploy-local"
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

deploy-local:
		@echo "=============================== Start Local Deployment ==============================="
		@echo "=================================== Requirements ====================================="
		@echo "1. Ensure you have Docker installed and service up and running in your system."
		@echo "2. Ensure you have Docker Compose installed and with permissions to execute it."
		sudo docker build -f api/devops/migrations/Dockerfile -t vcf-handler-api-migrations .
		sudo docker tag vcf-handler-api-migrations vcf-handler-api-migrations:0.1
		sudo docker build -f api/devops/api/Dockerfile -t vcf-handler-api .
		sudo docker tag vcf-handler-api vcf-handler-api:0.1
		sudo docker-compose -f api/devops/docker-compose.yml up -d

down-services:
		@echo "======================= Stopping Local Deployment Running Services==============================="
		sudo docker-compose -f api/devops/docker-compose.yml down