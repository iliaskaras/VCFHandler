FROM python:3.8.2

ARG migrations_user_id=9002
ARG migrations_group_id=9002

ARG vcf_handler_api_directory="/usr/local/vcf-handler-api"

ARG postgresql_connection_uri="postgresql+psycopg2://vcf_handler_api:123456@vcf-handler-api-postgresql:5432/vcf_handler_api"

ENV POSTGRESQL_CONNECTION_URI ${postgresql_connection_uri}

# Install Alembic.
RUN pip3 install \
  alembic==1.4.1 \
  psycopg2==2.8.4
#  sqlalchemy==1.3.13

# Create Migrations group and user.
RUN groupadd --system --gid ${migrations_group_id} migrationuser \
  && useradd --system --shell /usr/sbin/nologin --gid migrationuser --uid ${migrations_user_id} migrationuser

# Create VCF Handler API directory.
RUN mkdir -p ${vcf_handler_api_directory}/src

# Copy VCF Handler API migrations code.
COPY --chown=migrationuser:migrationuser "api/src" ${vcf_handler_api_directory}/src/
COPY --chown=migrationuser:migrationuser "api/alembic.ini" ${vcf_handler_api_directory}/

WORKDIR ${vcf_handler_api_directory}
ENV PYTHONPATH ${vcf_handler_api_directory}/src
# Set the migrationuser as the user to be used for running the ENTRYPOINT
USER migrationuser
ENTRYPOINT ["alembic", "-x", "postgresql_connection_uri=postgresql+psycopg2://vcf_handler_api:123456@vcf-handler-api-postgresql:5432/vcf_handler_api", "upgrade", "head"]
