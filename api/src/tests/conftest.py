import gzip
import os
import pytest
from application.infrastructure.configurations.enums import Environment
from application.infrastructure.configurations.models import ENV_VAR_NAME, Configuration


@pytest.fixture(scope='session')
def initialize_configuration() -> None:
    # Set Configuration environment to be equal to test environment.
    os.environ[ENV_VAR_NAME] = Environment.test.value

    Configuration.initialize()


@pytest.fixture
def setup_vcf_unzipped_file() -> None:
    """
    Sets up a fake vcf file before test and removes it after.
    """
    rows = [
        '##fileformat=VCFv4.2\n', '##reference=/ref/genomes/hg19/hg19.fa\n',
        '##FILTER=<ID=FAIL,Description="SNV quality < 100 or indel quality < 100 or DP < 8">\n',
        '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tNA12877 single 20180302\n',
        'chr1\t1\trs1\tT\tG\t1.1\tPASS\ttest\n',
        'chr2\t2\trs1\tT\tG\t1.1\tPASS\ttest\n',
        'chr3\t3\trs3\tA\tG\t2.2\tPASS\ttest\n',
        'chr4\t4\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
        'chr4\t5\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
        'chr4\t6\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
        'chr4\t7\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
    ]

    with open('test.vcf', 'w') as file:
        file.writelines(rows)

    yield

    os.remove("test.vcf")


@pytest.fixture
def setup_vcf_gzip_file() -> None:
    """
    Sets up a fake vcf gz file before test and removes it after.
    """
    byte_rows = [
        b'##fileformat=VCFv4.2\n',
        b'##reference=/ref/genomes/hg19/hg19.fa\n',
        b'##FILTER=<ID=FAIL,Description="SNV quality < 100 or indel quality < 100 or DP < 8">\n',
        b'#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tNA12877 single 20180302\n',
        b'chr1\t1\trs1\tT\tG\t1.1\tPASS\ttest\n',
        b'chr2\t2\trs1\tT\tG\t1.1\tPASS\ttest\n',
        b'chr3\t3\trs3\tA\tG\t2.2\tPASS\ttest\n',
        b'chr4\t4\trs4\tCAG\tC\t3.3\tPASS\ttest\n'
    ]

    with gzip.open('test.vcf.gz', 'wb') as file:
        file.writelines(byte_rows)

    yield

    os.remove("test.vcf.gz")
