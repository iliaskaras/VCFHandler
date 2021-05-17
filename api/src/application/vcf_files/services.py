from application.infrastructure.error.errors import InvalidArgumentError
from application.rest_api.vcf_files.enums import VCFHeader
from application.rest_api.vcf_files.operations import FilterVcfFile
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
