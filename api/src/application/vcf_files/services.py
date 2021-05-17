from typing import List, Dict, Union

from application.infrastructure.error.errors import InvalidArgumentError
from application.rest_api.vcf_files.enums import VCFHeader
from application.rest_api.vcf_files.operations import FilterVcfFile, AppendToVcfFile
from application.vcf_files.models import FilteredVcfRowsPage


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

        @:param vcf_file_path: The VCF file path to load.
        @:param filter_id: The source node.
        @:param page_size: The size of the page.
        @:param page_index: The index of the page.

        @:return: A FilteredVcfRowsPage.
        """

        if not filter_id:
            raise InvalidArgumentError('The Filter ID is required.')
        if page_size <= 0:
            raise InvalidArgumentError('The page size is required.')
        if page_index < 0:
            raise InvalidArgumentError('The page index is required.')

        vcf_filtered_rows = self.filter_vcf_file.run(
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
            data: List[Dict[str, Union[str, int]]] = None
    ) -> Dict[str, Union[int, str]]:
        """
        Handles data appending on a VCF File.

        @:param vcf_file_path: The VCF file path to load.
        @:param data: The list of data to append.

        @:return: A FilteredVcfRowsPage.
        """
        if not vcf_file_path:
            raise InvalidArgumentError('The VCF file path is required.')
        if not data:
            raise InvalidArgumentError('At least one row of data is required.')

        total_rows_added: int = self.append_to_vcf_file.run(
            vcf_file_path=vcf_file_path,
            data=data
        )

        return {
            "total_rows_added": total_rows_added,
            "file_path": vcf_file_path,
        }
