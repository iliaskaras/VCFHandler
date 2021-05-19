FROM python:3.8.2

ARG vcf_handler_api_user_id=9003
ARG vcf_handler_api_group_id=9003

# Environment variables such as salt, jwt_secret_key and postgresql_connection_uri should not be desplayed like that
# and instead be passed with some other mechanism that hides these information. Ansible could be used for example.
ARG vcf_handler_api_directory="/usr/local/vcf-handler-worker"
ARG vcf_files_api_environment="local"
ARG postgresql_connection_uri="postgresql+psycopg2://vcf_handler_api:123456@0.0.0.0:5432/vcf_handler_api"
ARG salt="salt"
ARG jwt_secret_key="6\xd8y\x80&q\xe2\xe2yO\xf5\xb5\xbf\xdbw."
ARG celery_broker_url="redis://localhost:6379"
ARG celery_result_backend="redis://localhost:6379"

ENV VCF_HANDLER_API_DIRECTORY ${vcf_handler_api_directory}
ENV VCF_FILES_API_ENVIRONMENT ${vcf_files_api_environment}
ENV POSTGRESQL_CONNECTION_URI ${postgresql_connection_uri}
ENV SALT ${salt}
ENV JWT_SECRET_KEY ${jwt_secret_key}
ENV CELERY_BROKER_URL ${celery_broker_url}
ENV CELERY_RESULT_BACKEND ${celery_result_backend}

# Create VCF Handler API group and user.
RUN groupadd --system --gid ${vcf_handler_api_group_id} vcfapiuser \
  && useradd --system --shell /usr/sbin/nologin \
             --gid vcfapiuser --uid ${vcf_handler_api_user_id} vcfapiuser

# Create VCF File Handler API directory.
RUN mkdir -p ${vcf_handler_api_directory}/src \
  && chown -R vcfapiuser:vcfapiuser ${vcf_handler_api_directory} \
  && chmod -R 770 ${vcf_handler_api_directory}

# Copy and install VCF File Handler API requirements.txt.
COPY --chown=vcfapiuser:vcfapiuser "api/requirements.txt" ${vcf_handler_api_directory}/
RUN pip3 install -r ${vcf_handler_api_directory}/requirements.txt

# Copy VCF File Handler API source code.
COPY --chown=vcfapiuser:vcfapiuser "api/src" ${vcf_handler_api_directory}/src/

# Run VCF File Handler API.
WORKDIR ${vcf_handler_api_directory}/src