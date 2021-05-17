from application.rest_api.vcf_files.operations import FilterVcfFile, AppendToVcfFile
from application.vcf_files.services import VcfFilePaginationService, AppendDataToVcfFileService


def vcf_file_pagination_service() -> VcfFilePaginationService:
    return VcfFilePaginationService(
        filter_vcf_file=FilterVcfFile(),
    )


def append_data_to_vcf_file_service() -> AppendDataToVcfFileService:
    return AppendDataToVcfFileService(
        append_to_vcf_file=AppendToVcfFile(),
    )
