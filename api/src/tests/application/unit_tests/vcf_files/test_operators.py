import copy
import gzip
import os
from unittest import mock

import pytest
from typing import Optional, List, Dict, Union
from unittest.mock import MagicMock

from application.infrastructure.error.errors import InvalidArgumentError, MultipleVCFHandlerBaseError, \
    VCFHandlerBaseError
from application.rest_api.vcf_files.enums import VCFHeader
from application.vcf_files.errors import VcfNoDataDeletedError, VcfDataUpdateError, VcfDataDeleteError, \
    VcfRowsByIdNotExistError, VcfDataAppendError
from application.vcf_files.models import VcfRow, FilteredVcfRowsPage, AppendRowsExecutionArtifact, \
    UpdatedRowsExecutionArtifact
from application.vcf_files.operations import FilterVcfFile, AppendToVcfFile, FilterOutRowsById, UpdateByIdVcfFile
from application.vcf_files.services import VcfFilePaginationService, AppendDataToVcfFileService, \
    FilterOutRowsByIdService, VcfFileUpdateByIdService


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


class TestFilterVcfFile:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.filter_vcf_file = FilterVcfFile()

    @pytest.mark.parametrize('vcf_file_path, headers, filter_id, page_size, page_index, errors', [
        # when_vcf_file_path_is_none
        (
                None, [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                'rs62635286', 10, 0, [InvalidArgumentError('The VCF file path is required.')]
        ),
        # when_headers_is_none
        (
                '/a/b/c/test.vcf', None,
                'rs62635286', 10, 0, [InvalidArgumentError('At least one VCF header is required.')]
        ),
        # when_filter_id_is_none
        (
                '/a/b/c/test.vcf', [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                None, 10, 0, [InvalidArgumentError('The Filter ID is required.')]
        ),
        # when_page_size_is_none
        (
                '/a/b/c/test.vcf', [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                'rs62635286', None, 0, [InvalidArgumentError('A page size above 0 is required.')]
        ),
        # when_page_size_is_below_zero
        (
                '/a/b/c/test.vcf', [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                'rs62635286', -1, 0, [InvalidArgumentError('A page size above 0 is required.')]
        ),
        # when_page_size_is_zero
        (
                '/a/b/c/test.vcf', [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                'rs62635286', 0, 0, [InvalidArgumentError('A page size above 0 is required.')]
        ),
        # when_page_index_is_none
        (
                '/a/b/c/test.vcf', [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                'rs62635286', 10, None, [InvalidArgumentError('A page index above or equal to zero is required.')]
        ),
        # when_page_index_is_below_zero
        (
                '/a/b/c/test.vcf', [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                'rs62635286', 10, -1, [InvalidArgumentError('A page index above or equal to zero is required.')]
        ),
        # when_page_index_is_below_zero_and_vcf_file_path_is_none
        (
                None, [VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                'rs62635286', 10, -1,
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('A page index above or equal to zero is required.'),
                ]
        ),
    ])
    def test_run_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            headers: Optional[List[VCFHeader]],
            filter_id: Optional[int],
            page_size: Optional[int],
            page_index: Optional[int],
            errors: List[VCFHandlerBaseError],
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.filter_vcf_file.run(
                vcf_file_path=vcf_file_path,
                headers=headers,
                filter_id=filter_id,
                page_size=page_size,
                page_index=page_index
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_run_gz_file_with_two_match_and_page_size_of_2(self, setup_vcf_gzip_file) -> None:
        page_size = 2
        page_index = 0
        vcf_file_path = 'test.vcf.gz'
        filter_id = 'rs1'

        expected_vcf_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr1',
                pos=1,
                identifier='rs1',
                ref='T',
                alt='G',
            ),
            VcfRow(
                chrom='chr2',
                pos=2,
                identifier='rs1',
                ref='T',
                alt='G',
            ),
        ]

        assert self.filter_vcf_file.run(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index
        ) == expected_vcf_rows

    def test_run_gz_file_with_one_match_and_page_size_of_2(self, setup_vcf_gzip_file) -> None:
        page_size = 2
        page_index = 0
        vcf_file_path = 'test.vcf.gz'
        filter_id = 'rs3'

        expected_vcf_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr3',
                pos=3,
                identifier='rs3',
                ref='A',
                alt='G',
            ),
        ]

        assert self.filter_vcf_file.run(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index
        ) == expected_vcf_rows

    def test_run_unzipped_file_with_two_match_and_page_size_of_2(self, setup_vcf_unzipped_file) -> None:
        page_size = 2
        page_index = 0
        vcf_file_path = 'test.vcf'
        filter_id = 'rs1'

        expected_vcf_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr1',
                pos=1,
                identifier='rs1',
                ref='T',
                alt='G',
            ),
            VcfRow(
                chrom='chr2',
                pos=2,
                identifier='rs1',
                ref='T',
                alt='G',
            ),
        ]

        assert self.filter_vcf_file.run(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index
        ) == expected_vcf_rows

    def test_run_unzipped_file_with_one_match_and_page_size_of_2(self, setup_vcf_unzipped_file) -> None:
        page_size = 2
        page_index = 0
        vcf_file_path = 'test.vcf'
        filter_id = 'rs3'

        expected_vcf_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr3',
                pos=3,
                identifier='rs3',
                ref='A',
                alt='G',
            ),
        ]

        assert self.filter_vcf_file.run(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index
        ) == expected_vcf_rows

    def test_run_raise_vcf_rows_by_id_not_exist_error(self, setup_vcf_unzipped_file) -> None:
        page_size = 2
        page_index = 0
        vcf_file_path = 'test.vcf'
        filter_id = 'rs'

        with pytest.raises(VcfRowsByIdNotExistError) as ex:
            self.filter_vcf_file.run(
                vcf_file_path=vcf_file_path,
                headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
                filter_id=filter_id,
                page_size=page_size,
                page_index=page_index
            )
        assert ex.typename == 'VcfRowsByIdNotExistError'
        assert ex.value.message == 'None rows found in VCF by the provided id:{}'.format(filter_id)

    def test_get_two_pages_of_total_4_rows(self, setup_vcf_unzipped_file) -> None:
        page_size = 2
        page_index = 0
        vcf_file_path = 'test.vcf'
        filter_id = 'rs4'

        expected_vcf_first_page_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr4',
                pos=4,
                identifier='rs4',
                ref='CAG',
                alt='C',
            ),
            VcfRow(
                chrom='chr4',
                pos=5,
                identifier='rs4',
                ref='CAG',
                alt='C',
            ),
        ]

        expected_vcf_second_page_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr4',
                pos=6,
                identifier='rs4',
                ref='CAG',
                alt='C',
            ),
            VcfRow(
                chrom='chr4',
                pos=7,
                identifier='rs4',
                ref='CAG',
                alt='C',
            ),
        ]

        assert self.filter_vcf_file.run(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index
        ) == expected_vcf_first_page_rows

        assert self.filter_vcf_file.run(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index + 1
        ) == expected_vcf_second_page_rows


class TestAppendToVcfFile:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.append_vcf_file = AppendToVcfFile()

    @pytest.mark.parametrize('vcf_file_path, vcf_rows, errors', [
        # when_vcf_file_path_is_none
        (
                None,
                [
                    VcfRow(
                        chrom='chr8',
                        pos=8,
                        identifier='rs8',
                        ref='T',
                        alt='G',
                    ),
                    VcfRow(
                        chrom='chr9',
                        pos=9,
                        identifier='rs9',
                        ref='T',
                        alt='G',
                    ),
                ],
                [InvalidArgumentError('The VCF file path is required.')]
        ),
        # when_vcf_row_is_none
        (
                '/a/b/c/test.vcf',
                None,
                [InvalidArgumentError('At least one row of data is required.')]
        ),
        # when_vcf_row_is_empty_list
        (
                '/a/b/c/test.vcf',
                [],
                [InvalidArgumentError('At least one row of data is required.')]
        ),
    ])
    def test_run_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            vcf_rows: Optional[List[VcfRow]],
            errors: List[VCFHandlerBaseError],
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.append_vcf_file.run(
                vcf_file_path=vcf_file_path,
                vcf_rows=vcf_rows,
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_run_append_two_rows(self, setup_vcf_unzipped_file) -> None:
        vcf_file_path = 'test.vcf'

        vcf_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr8',
                pos=8,
                identifier='rs8',
                ref='T',
                alt='G',
            ),
            VcfRow(
                chrom='chr9',
                pos=9,
                identifier='rs9',
                ref='T',
                alt='G',
            ),
        ]

        with open(vcf_file_path, 'r') as file:
            before_append_length = len([row for row in file if not row.startswith('##')])

        assert self.append_vcf_file.run(
            vcf_file_path=vcf_file_path,
            vcf_rows=vcf_rows,
        ) == 2

        with open(vcf_file_path, 'r') as file:
            after_append_length = len([row for row in file if not row.startswith('##')])

        assert after_append_length == before_append_length + 2

    @mock.patch('application.vcf_files.operations.gzip.open')
    def test_raise_vcf_data_append_error(self, mock_gzip_open, setup_vcf_unzipped_file) -> None:
        vcf_file_path = 'test.vcf.gz'

        vcf_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr8',
                pos=8,
                identifier='rs8',
                ref='T',
                alt='G',
            ),
            VcfRow(
                chrom='chr9',
                pos=9,
                identifier='rs9',
                ref='T',
                alt='G',
            ),
        ]

        mock_gzip_open.side_effect = Exception('error')

        with pytest.raises(VcfDataAppendError) as ex:
            self.append_vcf_file.run(
                vcf_file_path=vcf_file_path,
                vcf_rows=vcf_rows,
            )
        assert ex.value.message == 'error'
        assert ex.typename == 'VcfDataAppendError'

    def test_run_append_two_rows_to_gz_file(self, setup_vcf_gzip_file) -> None:
        vcf_file_path = 'test.vcf.gz'

        vcf_rows: List[VcfRow] = [
            VcfRow(
                chrom='chr8',
                pos=8,
                identifier='rs8',
                ref='T',
                alt='G',
            ),
            VcfRow(
                chrom='chr9',
                pos=9,
                identifier='rs9',
                ref='T',
                alt='G',
            ),
        ]

        with gzip.open(vcf_file_path, 'r') as file:
            before_append_length = len([row for row in file if not row.startswith(b'##')])

        assert self.append_vcf_file.run(
            vcf_file_path=vcf_file_path,
            vcf_rows=vcf_rows,
        ) == 2

        with gzip.open(vcf_file_path, 'r') as file:
            after_append_length = len([row for row in file if not row.startswith(b'##')])

        assert after_append_length == before_append_length + 2


class TestFilterOutRowsById:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.filter_out_rows_by_id = FilterOutRowsById()

    @pytest.mark.parametrize('vcf_file_path, filter_id, errors', [
        # when_vcf_file_path_is_none
        (
                None,
                'rs62635286',
                [InvalidArgumentError('The VCF file path is required.')]
        ),
        # when_filter_id_is_none
        (
                '/a/b/c/test.vcf',
                None,
                [InvalidArgumentError('The filter id is required.')]
        ),
        # when_filter_id_and_vcf_file_path_is_none
        (
                None,
                None,
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('The filter id is required.')
                ]
        ),
    ])
    def test_run_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            filter_id: Optional[str],
            errors: List[VCFHandlerBaseError],
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.filter_out_rows_by_id.run(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_run_filter_out_by_id(self, setup_vcf_unzipped_file) -> None:
        vcf_file_path = 'test.vcf'
        filter_id = 'rs1'

        with open(vcf_file_path, 'r') as file:
            before_remove_length = len([row for row in file if not row.startswith('##')])

        # There is only 1 with that id to be deleted.
        assert self.filter_out_rows_by_id.run(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
        ) == 2

        with open(vcf_file_path, 'r') as file:
            after_remove_length = len([row for row in file if not row.startswith('##')])

        assert after_remove_length == before_remove_length - 2

    def test_run_filter_out_by_id_in_gz_file(self, setup_vcf_gzip_file) -> None:
        vcf_file_path = 'test.vcf.gz'
        filter_id = 'rs1'

        with gzip.open(vcf_file_path, 'r') as file:
            before_remove_length = len([row for row in file if not row.startswith(b'##')])

        # There is only 1 with that id to be deleted.
        assert self.filter_out_rows_by_id.run(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
        ) == 2

        with gzip.open(vcf_file_path, 'r') as file:
            after_remove_length = len([row for row in file if not row.startswith(b'##')])

        assert after_remove_length == before_remove_length - 2

    @mock.patch('application.vcf_files.operations.gzip.open')
    def test_raise_vcf_data_append_error(self, mock_gzip_open, setup_vcf_unzipped_file) -> None:
        vcf_file_path = 'test.vcf.gz'
        filter_id = 'rs1'

        mock_gzip_open.side_effect = Exception('error')

        with pytest.raises(VcfDataDeleteError) as ex:
            self.filter_out_rows_by_id.run(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
            )
        assert ex.value.message == 'error'
        assert ex.typename == 'VcfDataDeleteError'


class TestUpdateByIdVcfFile:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.update_by_id_vcf_file = UpdateByIdVcfFile()

    @pytest.mark.parametrize('vcf_file_path, filter_id, data, errors', [
        # when_vcf_file_path_is_none
        (
                None,
                'rs62635286',
                VcfRow(
                    chrom='chr1',
                    pos=1,
                    identifier='rs1',
                    ref='T',
                    alt='G',
                ),
                [InvalidArgumentError('The VCF file path is required.')]
        ),
        # when_filter_id_is_none
        (
                '/a/b/c/test.vcf',
                None,
                VcfRow(
                    chrom='chr1',
                    pos=1,
                    identifier='rs1',
                    ref='T',
                    alt='G',
                ),
                [InvalidArgumentError('The filter id is required.')]
        ),
        # when_vcf_row_is_none
        (
                '/a/b/c/test.vcf',
                'rs62635286',
                None,
                [InvalidArgumentError('Data are required.')]
        ),
        # when_filter_id_and_vcf_file_path_is_none
        (
                None,
                None,
                VcfRow(
                    chrom='chr1',
                    pos=1,
                    identifier='rs1',
                    ref='T',
                    alt='G',
                ),
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('The filter id is required.')
                ]
        ),
    ])
    def test_run_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            filter_id: Optional[str],
            data: Optional[VcfRow],
            errors: List[VCFHandlerBaseError],
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.update_by_id_vcf_file.run(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
                data=data
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_run_update_by_id(self, setup_vcf_unzipped_file) -> None:
        vcf_file_path = 'test.vcf'
        filter_id = 'rs1'
        data = VcfRow(
            chrom='chr5',
            pos=100,
            identifier='rs1',
            ref='T',
            alt='G',
        )

        with open(vcf_file_path, 'r') as file:
            before_update_length = len([row for row in file if not row.startswith('##')])

        # There is only 1 with that id to be deleted.
        assert self.update_by_id_vcf_file.run(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
            data=copy.copy(data)
        ) == 2

        with open(vcf_file_path, 'r') as file:
            after_update_length = [row for row in file if not row.startswith('##')]

        assert len(after_update_length) == before_update_length

        updated_row = after_update_length[1].split('\t')[:5]
        updated_data1 = VcfRow(
            chrom=updated_row[0],
            pos=int(updated_row[1]),
            identifier=updated_row[2],
            ref=updated_row[3],
            alt=updated_row[4],
        )
        updated_row = after_update_length[2].split('\t')[:5]
        updated_data2 = VcfRow(
            chrom=updated_row[0],
            pos=int(updated_row[1]),
            identifier=updated_row[2],
            ref=updated_row[3],
            alt=updated_row[4],
        )
        assert updated_data1 == data
        assert updated_data2 == data

    def test_run_update_by_id_gz_file(self, setup_vcf_gzip_file) -> None:
        vcf_file_path = 'test.vcf.gz'
        filter_id = 'rs1'
        data = VcfRow(
            chrom='chr5',
            pos=100,
            identifier='rs1',
            ref='T',
            alt='G',
        )

        with gzip.open(vcf_file_path, 'r') as file:
            before_update_length = len([row for row in file if not row.startswith(b'##')])

        # There is only 1 with that id to be deleted.
        assert self.update_by_id_vcf_file.run(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
            data=copy.copy(data)
        ) == 2

        with gzip.open(vcf_file_path, 'r') as file:
            after_update_length = [row for row in file if not row.startswith(b'##')]

        assert len(after_update_length) == before_update_length

        updated_row = after_update_length[1].split(b'\t')[:5]
        updated_data1 = VcfRow(
            chrom=updated_row[0].decode("utf-8"),
            pos=int(updated_row[1]),
            identifier=updated_row[2].decode("utf-8"),
            ref=updated_row[3].decode("utf-8"),
            alt=updated_row[4].decode("utf-8"),
        )
        updated_row = after_update_length[2].split(b'\t')[:5]
        updated_data2 = VcfRow(
            chrom=updated_row[0].decode("utf-8"),
            pos=int(updated_row[1]),
            identifier=updated_row[2].decode("utf-8"),
            ref=updated_row[3].decode("utf-8"),
            alt=updated_row[4].decode("utf-8"),
        )
        assert updated_data1 == data
        assert updated_data2 == data

    @mock.patch('application.vcf_files.operations.gzip.open')
    def test_raise_vcf_data_append_error(self, mock_gzip_open, setup_vcf_unzipped_file) -> None:
        vcf_file_path = 'test.vcf.gz'
        filter_id = 'rs1'
        data = VcfRow(
            chrom='chr5',
            pos=100,
            identifier='rs1',
            ref='T',
            alt='G',
        )

        mock_gzip_open.side_effect = Exception('error')

        with pytest.raises(VcfDataUpdateError) as ex:
            self.update_by_id_vcf_file.run(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
                data=data
            )
        assert ex.value.message == 'error'
        assert ex.typename == 'VcfDataUpdateError'
