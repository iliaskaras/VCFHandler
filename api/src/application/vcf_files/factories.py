from application.vcf_files.operations import FilterVcfFile, AppendToVcfFile, FilterOutRowsById, \
    UpdateByIdVcfFile, AsyncFilterOutRowsById
from application.vcf_files.services import VcfFilePaginationService, AppendDataToVcfFileService, \
    FilterOutRowsByIdService, VcfFileUpdateByIdService, AsyncFilterOutRowsByIdService


def vcf_file_pagination_service() -> VcfFilePaginationService:
    return VcfFilePaginationService(
        filter_vcf_file=FilterVcfFile(),
    )


def append_data_to_vcf_file_service() -> AppendDataToVcfFileService:
    return AppendDataToVcfFileService(
        append_to_vcf_file=AppendToVcfFile(),
    )


def filter_out_rows_by_id_service() -> FilterOutRowsByIdService:
    return FilterOutRowsByIdService(
        filter_out_rows_by_id=FilterOutRowsById(),
    )


def async_filter_out_rows_by_id_service() -> AsyncFilterOutRowsByIdService:
    return AsyncFilterOutRowsByIdService(
        filter_out_rows_by_id=AsyncFilterOutRowsById(),
    )


def vcf_file_update_by_id_service() -> VcfFileUpdateByIdService:
    return VcfFileUpdateByIdService(
        update_by_id_vcf_file=UpdateByIdVcfFile(),
    )
