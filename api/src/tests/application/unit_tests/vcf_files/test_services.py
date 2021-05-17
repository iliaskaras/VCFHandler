import pytest
from typing import Optional, List, Dict, Union
from unittest.mock import MagicMock

from application.infrastructure.error.errors import InvalidArgumentError, MultipleVCFHandlerBaseError, \
    VCFHandlerBaseError
from application.rest_api.vcf_files.enums import VCFHeader
from application.vcf_files.errors import VcfNoDataDeletedError, VcfDataUpdateError
from application.vcf_files.models import VcfRow, FilteredVcfRowsPage, AppendRowsExecutionArtifact, \
    UpdatedRowsExecutionArtifact
from application.vcf_files.services import VcfFilePaginationService, AppendDataToVcfFileService, \
    FilterOutRowsByIdService, VcfFileUpdateByIdService


class TestGetCategoriesService:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.mock_filter_vcf_file = MagicMock()

        self.vcf_file_pagination_service = VcfFilePaginationService(self.mock_filter_vcf_file)

    @pytest.mark.parametrize('vcf_file_path, filter_id, page_size, page_index, errors', [
        # when_vcf_file_path_is_none
        (None, 'rs62635286', 10, 0, [InvalidArgumentError('The VCF file path is required.')]),
        # when_filter_id_is_none
        ('/a/b/c/test.vcf', None, 10, 0, [InvalidArgumentError('The Filter ID is required.')]),
        # when_page_size_is_none
        ('/a/b/c/test.vcf', 'rs62635286', None, 0, [InvalidArgumentError('A page size above 0 is required.')]),
        # when_page_size_is_below_zero
        ('/a/b/c/test.vcf', 'rs62635286', -1, 0, [InvalidArgumentError('A page size above 0 is required.')]),
        # when_page_size_is_zero
        ('/a/b/c/test.vcf', 'rs62635286', 0, 0, [InvalidArgumentError('A page size above 0 is required.')]),
        # when_page_index_is_none
        (
                '/a/b/c/test.vcf', 'rs62635286', 10, None,
                [InvalidArgumentError('A page index above or equal to zero is required.')]
        ),
        # when_page_index_is_below_zero
        (
                '/a/b/c/test.vcf', 'rs62635286', 10, -1,
                [InvalidArgumentError('A page index above or equal to zero is required.')]
        ),
        # when_page_index_is_below_zero_and_vcf_file_path_is_none
        (
                None, 'rs62635286', 10, -1,
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('A page index above or equal to zero is required.'),
                ]
        ),
    ])
    def test_apply_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            filter_id: Optional[str],
            page_size: Optional[int],
            page_index: Optional[int],
            errors: List[VCFHandlerBaseError]
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.vcf_file_pagination_service.apply(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
                page_size=page_size,
                page_index=page_index
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_apply(self) -> None:
        vcf_filtered_rows: List[VcfRow] = [
            VcfRow(chrom='chr7', pos=24966446, identifier='rs123', ref='C', alt='A'),
            VcfRow(chrom='chr8', pos=24966447, identifier='rs123', ref='C', alt='A'),
        ]
        page_size = 10
        page_index = 0
        vcf_file_path = '/a/b/c/test.vcf'
        filter_id = 'rs62635286'

        expected_filtered_vcf_rows_page: FilteredVcfRowsPage = FilteredVcfRowsPage(
            page_size=page_size,
            page_index=page_index,
            total=2,
            filtered_id=filter_id,
            results=vcf_filtered_rows
        )

        self.mock_filter_vcf_file.run.return_value = vcf_filtered_rows

        assert self.vcf_file_pagination_service.apply(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index
        ) == expected_filtered_vcf_rows_page

        self.mock_filter_vcf_file.run.assert_called_once_with(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index,
        )


class TestAppendDataToVcfFileService:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.mock_append_to_vcf_file = MagicMock()

        self.append_data_to_vcf_file_service = AppendDataToVcfFileService(self.mock_append_to_vcf_file)

    @pytest.mark.parametrize('vcf_file_path, data, errors', [
        # when_vcf_file_path_is_none
        (
                None,
                [
                    VcfRow(chrom="chr22", pos=1000, alt="T", ref="G", identifier='rs12'),
                    VcfRow(chrom="chr22", pos=1001, alt="T", ref="G", identifier='rs12'),
                ],
                [InvalidArgumentError('The VCF file path is required.')]
        ),
        # when_data_is_none
        (
                '/a/b/c/test.vcf',
                None,
                [InvalidArgumentError('At least one row of data is required.')]
        ),
        # when_data_is_empty_list
        (
                '/a/b/c/test.vcf',
                [],
                [InvalidArgumentError('At least one row of data is required.')]
        ),
        # when_vcf_file_path_and_data_are_none
        (
                None,
                None,
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('At least one row of data is required.')
                ]
        ),
    ])
    def test_apply_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            data: Optional[List[Dict[str, Union[str, int]]]],
            errors: List[VCFHandlerBaseError]
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.append_data_to_vcf_file_service.apply(
                vcf_file_path=vcf_file_path,
                vcf_rows=data,
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_apply(self) -> None:
        vcf_filtered_rows: List[VcfRow] = [
            VcfRow(chrom='chr7', pos=24966446, identifier='rs123', ref='C', alt='A'),
            VcfRow(chrom='chr8', pos=24966447, identifier='rs123', ref='C', alt='A'),
        ]
        vcf_file_path = '/a/b/c/test.vcf'

        expected_append_rows_execution_artifact: AppendRowsExecutionArtifact = AppendRowsExecutionArtifact(
            total_rows_added=2,
            file_path='/a/b/c/test.vcf',
        )

        self.mock_append_to_vcf_file.run.return_value = 2

        assert self.append_data_to_vcf_file_service.apply(
            vcf_file_path=vcf_file_path,
            vcf_rows=vcf_filtered_rows,
        ) == expected_append_rows_execution_artifact

        self.mock_append_to_vcf_file.run.assert_called_once_with(
            vcf_file_path=vcf_file_path,
            vcf_rows=vcf_filtered_rows,
        )


class TestFilterOutRowsByIdService:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.mock_filter_out_rows_by_id = MagicMock()

        self.filter_out_rows_by_id_service = FilterOutRowsByIdService(self.mock_filter_out_rows_by_id)

    @pytest.mark.parametrize('vcf_file_path, filter_id, errors', [
        # when_vcf_file_path_is_none
        (None, 'rs62635286', [InvalidArgumentError('The VCF file path is required.')]),
        # when_filter_id_is_none
        ('/a/b/c/test.vcf', None, [InvalidArgumentError('The Filter ID is required.')]),
        # when_vcf_file_path_and_filter_id_are_none
        (
                None,
                None,
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('The Filter ID is required.')
                ]
        ),
    ])
    def test_apply_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            filter_id: Optional[str],
            errors: List[VCFHandlerBaseError]
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.filter_out_rows_by_id_service.apply(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_apply(self) -> None:
        filter_id = 'rs62635286'
        vcf_file_path = '/a/b/c/test.vcf'

        self.mock_filter_out_rows_by_id.run.return_value = 2

        assert self.filter_out_rows_by_id_service.apply(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
        ) is None

        self.mock_filter_out_rows_by_id.run.assert_called_once_with(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
        )

    def test_apply_raise_vcf_no_data_deleted_error(self) -> None:
        filter_id = 'rs62635286'
        vcf_file_path = '/a/b/c/test.vcf'

        self.mock_filter_out_rows_by_id.run.return_value = 0

        with pytest.raises(VcfNoDataDeletedError) as ex:
            self.filter_out_rows_by_id_service.apply(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
            )

        assert ex.value.message == "No data found for deletion"
        assert ex.value.error_type == "VcfDataDeleteError"

        self.mock_filter_out_rows_by_id.run.assert_called_once_with(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
        )


class TestVcfFileUpdateByIdService:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.mock_update_by_id_vcf_file = MagicMock()

        self.vcf_file_update_by_id_service = VcfFileUpdateByIdService(self.mock_update_by_id_vcf_file)

    @pytest.mark.parametrize('vcf_file_path, filter_id, data, errors', [
        # when_vcf_file_path_is_none
        (
                None,
                'rs62635286',
                VcfRow(chrom="chr22", pos=1000, alt="T", ref="G", identifier='rs12'),
                [InvalidArgumentError('The VCF file path is required.')]),
        # when_filter_id_is_none
        (
                '/a/b/c/test.vcf',
                None,
                VcfRow(chrom="chr22", pos=1000, alt="T", ref="G", identifier='rs12'),
                [InvalidArgumentError('The Filter ID is required.')]
        ),
        # when_data_is_none
        (
                '/a/b/c/test.vcf',
                'rs62635286',
                None,
                [InvalidArgumentError('Data are required.')]
        ),
        # when_vcf_file_path_and_filter_id_are_none
        (
                None,
                None,
                VcfRow(chrom="chr22", pos=1000, alt="T", ref="G", identifier='rs12'),
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('The Filter ID is required.')
                ]
        ),
        # when_all_are_none
        (
                None,
                None,
                None,
                [
                    InvalidArgumentError('The VCF file path is required.'),
                    InvalidArgumentError('The Filter ID is required.'),
                    InvalidArgumentError('Data are required.')
                ]
        ),
    ])
    def test_apply_with_invalid_arguments(
            self,
            vcf_file_path: Optional[str],
            filter_id: Optional[str],
            data: Optional[VcfRow],
            errors: List[VCFHandlerBaseError]
    ) -> None:
        with pytest.raises(MultipleVCFHandlerBaseError) as ex:
            self.vcf_file_update_by_id_service.apply(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
                data=data
            )
        for returned_error, expected_error in zip(ex.value.errors, errors):
            assert returned_error.__dict__ == expected_error.__dict__

    def test_apply(self) -> None:
        filter_id = 'rs62635286'
        vcf_file_path = '/a/b/c/test.vcf'
        data = VcfRow(chrom="chr22", pos=1000, alt="T", ref="G", identifier='rs12')

        self.mock_update_by_id_vcf_file.run.return_value = 1

        expected_updated_rows_execution_artifact: UpdatedRowsExecutionArtifact = UpdatedRowsExecutionArtifact(
            total_rows_updated=1,
            file_path='/a/b/c/test.vcf',
        )

        assert self.vcf_file_update_by_id_service.apply(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
            data=data
        ) == expected_updated_rows_execution_artifact

        self.mock_update_by_id_vcf_file.run.assert_called_once_with(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
            data=data
        )

    def test_apply_raise_vcf_data_update_error(self) -> None:
        filter_id = 'rs62635286'
        vcf_file_path = '/a/b/c/test.vcf'
        data = VcfRow(chrom="chr22", pos=1000, alt="T", ref="G", identifier='rs12')

        self.mock_update_by_id_vcf_file.run.return_value = 0

        with pytest.raises(VcfDataUpdateError) as ex:
            self.vcf_file_update_by_id_service.apply(
                vcf_file_path=vcf_file_path,
                filter_id=filter_id,
                data=data
            )

        assert ex.value.message == "No data found for update"
        assert ex.value.error_type == "VcfDataUpdateError"

        self.mock_update_by_id_vcf_file.run.assert_called_once_with(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
            data=data
        )

