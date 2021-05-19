from typing import List

from application.infrastructure.error.errors import InvalidArgumentError, MultipleVCFHandlerBaseError
from application.rest_api.vcf_files.enums import VCFHeader
from application.vcf_files.operations import FilterVcfFile, AppendToVcfFile, FilterOutRowsById, \
    UpdateByIdVcfFile, AsyncFilterOutRowsById
from application.vcf_files.errors import VcfNoDataDeletedError, VcfDataUpdateError
from application.vcf_files.models import FilteredVcfRowsPage, VcfRow, AppendRowsExecutionArtifact, \
    UpdatedRowsExecutionArtifact


class VcfFilePaginationService:

    def __init__(
            self,
            filter_vcf_file: FilterVcfFile,
    ):
        self.filter_vcf_file = filter_vcf_file

    def apply(
            self,
            vcf_file_path: str,
            filter_id: str,
            page_size: int = 10,
            page_index: int = 0
    ) -> FilteredVcfRowsPage:
        """
        VCF File pagination Service.

        :param vcf_file_path: The VCF file path to load.
        :param filter_id: The filter id.
        :param page_size: The size of the page.
        :param page_index: The index of the page.

        :return: A FilteredVcfRowsPage.

        :raise: InvalidArgumentError: In case an invalid argument is provided.
        """
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The Filter ID is required.'))
        if page_size is None or page_size <= 0:
            errors.append(InvalidArgumentError('A page size above 0 is required.'))
        if page_index is None or page_index < 0:
            errors.append(InvalidArgumentError('A page index above or equal to zero is required.'))

        if errors.errors:
            raise errors

        vcf_filtered_rows: List[VcfRow] = self.filter_vcf_file.run(
            vcf_file_path=vcf_file_path,
            headers=[VCFHeader.chrom, VCFHeader.pos, VCFHeader.alt, VCFHeader.ref, VCFHeader.id],
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index,
        )

        return FilteredVcfRowsPage(
            page_size=page_size,
            page_index=page_index,
            total=len(vcf_filtered_rows),
            filtered_id=filter_id,
            results=vcf_filtered_rows
        )


class AppendDataToVcfFileService:

    def __init__(
            self,
            append_to_vcf_file: AppendToVcfFile,
    ):
        self.append_to_vcf_file = append_to_vcf_file

    def apply(
            self,
            vcf_file_path: str,
            vcf_rows: List[VcfRow] = None
    ) -> AppendRowsExecutionArtifact:
        """
        Handles data appending on a VCF File.

        :param vcf_file_path: The VCF file path to load.
        :param vcf_rows: The list of VcfRows to append.

        :return: The VCF file rows append execution artifact.

        :raise: InvalidArgumentError: In case an invalid argument is provided.
        """
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not vcf_rows:
            errors.append(InvalidArgumentError('At least one row of data is required.'))

        if errors.errors:
            raise errors

        total_rows_added: int = self.append_to_vcf_file.run(
            vcf_file_path=vcf_file_path,
            vcf_rows=vcf_rows
        )

        return AppendRowsExecutionArtifact(
            total_rows_added=total_rows_added,
            file_path=vcf_file_path
        )


class FilterOutRowsByIdService:

    def __init__(
            self,
            filter_out_rows_by_id: FilterOutRowsById,
    ):
        self.filter_out_rows_by_id = filter_out_rows_by_id

    def apply(
            self,
            vcf_file_path: str,
            filter_id: str,
    ) -> None:
        """
        Handles data appending on a VCF File.

        :param vcf_file_path: The VCF file path to load.
        :param filter_id: The filter id.

        :raise: InvalidArgumentError: In case an invalid argument is provided.
                VcfNoDataDeletedError: In case no data were found to delete.
        """
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The Filter ID is required.'))

        if errors.errors:
            raise errors

        deleted_rows: int = self.filter_out_rows_by_id.run(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
        )

        if deleted_rows == 0:
            raise VcfNoDataDeletedError("No data found for deletion")


class AsyncFilterOutRowsByIdService:

    def __init__(
            self,
            filter_out_rows_by_id: AsyncFilterOutRowsById,
    ):
        self.filter_out_rows_by_id = filter_out_rows_by_id

    def apply(
            self,
            vcf_file_path: str,
            filter_id: str,
    ) -> None:
        """
        Handles data appending on a VCF File.

        :param vcf_file_path: The VCF file path to load.
        :param filter_id: The filter id.

        :raise: InvalidArgumentError: In case an invalid argument is provided.
                VcfNoDataDeletedError: In case no data were found to delete.
        """
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The Filter ID is required.'))

        if errors.errors:
            raise errors

        deleted_rows: int = self.filter_out_rows_by_id.run.delay(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
        )

        if deleted_rows == 0:
            raise VcfNoDataDeletedError("No data found for deletion")


class VcfFileUpdateByIdService:

    def __init__(
            self,
            update_by_id_vcf_file: UpdateByIdVcfFile,
    ):
        self.update_by_id_vcf_file = update_by_id_vcf_file

    def apply(
            self,
            vcf_file_path: str,
            filter_id: str,
            data: VcfRow = None
    ) -> UpdatedRowsExecutionArtifact:
        """
        VCF File update Service.

        :param vcf_file_path: The VCF file path to load.
        :param filter_id: The filter id.
        :param data: The data to update file by id.

        :return: The VCF file rows update execution artifact.

        :raise: InvalidArgumentError: In case an invalid argument is provided.
        """
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The Filter ID is required.'))
        if not data:
            errors.append(InvalidArgumentError('Data are required.'))

        if errors.errors:
            raise errors

        updated_rows = self.update_by_id_vcf_file.run(
            vcf_file_path=vcf_file_path,
            filter_id=filter_id,
            data=data
        )

        if updated_rows == 0:
            raise VcfDataUpdateError("No data found for update")

        return UpdatedRowsExecutionArtifact(
            total_rows_updated=updated_rows,
            file_path=vcf_file_path
        )
