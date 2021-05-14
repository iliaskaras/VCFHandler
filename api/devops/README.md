# VCFHandler DevOps
##DevOps related files for the VCFHandler REST API

###Prerequisites:
- You must have installed Docker and Docker-compose in your OS.

###Steps to run the Dockerfiles:

1. cd to the VCFHandler/api directory.
2. docker build -f devops/postgresql/Dockerfile -t vcf-handler-api-postgresql .
3. docker tag vcf-handler-api-postgresql vcf-handler-api-postgresql:0.1
4. sudo docker build -f devops/migrations/Dockerfile -t vcf-handler-api-migrations .
5. docker tag vcf-handler-api-migrations vcf-handler-api-migrations:0.1
6. docker-compose up -d