from application.rest_api.vcf_files.operations import FilterVcfFile
from application.vcf_files.services import VcfFilePaginationService


def vcf_file_pagination_service() -> VcfFilePaginationService:
    return VcfFilePaginationService(
        filter_vcf_file=FilterVcfFile(),
    )
