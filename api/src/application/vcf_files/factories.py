from application.rest_api.vcf_files.operations import FilterVcfFile, AppendToVcfFile, FilterOutByIdVcfFile
from application.vcf_files.services import VcfFilePaginationService, AppendDataToVcfFileService, \
    FilterOutByIdVcfFileService


def vcf_file_pagination_service() -> VcfFilePaginationService:
    return VcfFilePaginationService(
        filter_vcf_file=FilterVcfFile(),
    )


def append_data_to_vcf_file_service() -> AppendDataToVcfFileService:
    return AppendDataToVcfFileService(
        append_to_vcf_file=AppendToVcfFile(),
    )


def vcf_file_filter_out_by_id_service() -> FilterOutByIdVcfFileService:
    return FilterOutByIdVcfFileService(
        filter_out_by_id_vcf_file=FilterOutByIdVcfFile(),
    )
