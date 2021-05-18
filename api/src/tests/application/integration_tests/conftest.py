import os
from application.infrastructure.configurations.enums import Environment
from application.infrastructure.configurations.models import ENV_VAR_NAME, Configuration
from datetime import timedelta
from flask import Flask

import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from application.authentication.models import JwtIdentity
from application.factories import vcf_handler_api
from application.user.enums import Permission


@pytest.fixture(scope='session')
def initialize_configuration() -> None:
    # Set Configuration environment to be equal to test environment.
    os.environ[ENV_VAR_NAME] = Environment.test.value

    Configuration.initialize()


@pytest.fixture()
def access_token_read_permission(flask_app) -> str:
    jwt_identity: JwtIdentity = JwtIdentity(
        user_id='1',
        user_permission=Permission.read.value
    )
    with flask_app.app_context():
        access_token = create_access_token(
            identity=jwt_identity.__dict__,
            expires_delta=timedelta(
                seconds=1000
            )
        )
    return access_token


@pytest.fixture()
def access_token_execute_permission(flask_app) -> str:
    jwt_identity: JwtIdentity = JwtIdentity(
        user_id='1',
        user_permission=Permission.execute.value
    )
    with flask_app.app_context():
        access_token = create_access_token(
            identity=jwt_identity.__dict__,
            expires_delta=timedelta(
                seconds=1000
            )
        )
    return access_token


@pytest.fixture(scope='function')
def client(initialize_configuration) -> FlaskClient:
    """
    Fixture for a FlaskClient which is used for creating requests to a test
    application.

    @return: A FlaskClient instance.
    """

    flask_application = vcf_handler_api('TESTING')
    flask_application.config['TESTING'] = True
    flask_application.config['PROPAGATE_EXCEPTIONS'] = False

    client_instance = flask_application.test_client()

    yield client_instance


@pytest.fixture(scope='function')
def flask_app(initialize_configuration) -> Flask:
    """
    Fixture for making a Flask instance, to be able to access application context manager.
    This is not possible with a FlaskClient, and we need the context manager for creating
    JWT tokens when is required.

    @return: A Flask instance.
    """

    flask_application = vcf_handler_api('TESTING')
    flask_application.config['TESTING'] = True
    flask_application.config['PROPAGATE_EXCEPTIONS'] = False

    return flask_application

#
# @pytest.fixture
# def setup_vcf_unzipped_file() -> None:
#     """
#     Sets up a fake vcf file before test and removes it after.
#     """
#     rows = [
#         '##fileformat=VCFv4.2\n', '##reference=/ref/genomes/hg19/hg19.fa\n',
#         '##FILTER=<ID=FAIL,Description="SNV quality < 100 or indel quality < 100 or DP < 8">\n',
#         '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tNA12877 single 20180302\n',
#         'chr1\t1\trs1\tT\tG\t1.1\tPASS\ttest\n',
#         'chr2\t2\trs1\tT\tG\t1.1\tPASS\ttest\n',
#         'chr3\t3\trs3\tA\tG\t2.2\tPASS\ttest\n',
#         'chr4\t4\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
#         'chr4\t5\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
#         'chr4\t6\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
#         'chr4\t7\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
#     ]
# 
#     with open('test.vcf', 'w') as file:
#         file.writelines(rows)
# 
#     yield
# 
#     os.remove("test.vcf")
# 
# 
# @pytest.fixture
# def setup_vcf_gzip_file() -> None:
#     """
#     Sets up a fake vcf gz file before test and removes it after.
#     """
#     byte_rows = [
#         b'##fileformat=VCFv4.2\n',
#         b'##reference=/ref/genomes/hg19/hg19.fa\n',
#         b'##FILTER=<ID=FAIL,Description="SNV quality < 100 or indel quality < 100 or DP < 8">\n',
#         b'#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tNA12877 single 20180302\n',
#         b'chr1\t1\trs1\tT\tG\t1.1\tPASS\ttest\n',
#         b'chr2\t2\trs1\tT\tG\t1.1\tPASS\ttest\n',
#         b'chr3\t3\trs3\tA\tG\t2.2\tPASS\ttest\n',
#         b'chr4\t4\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
#     ]
# 
#     with gzip.open('test.vcf.gz', 'wb') as file:
#         file.writelines(byte_rows)
# 
#     yield
# 
#     os.remove("test.vcf.gz")
