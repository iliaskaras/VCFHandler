from typing import Dict, List, Union

from flask_restplus import Resource
from flask_accept import accept

from application.authentication.decorators import guard
from application.rest_api.decorators import map_request, map_response, map_errors, add_etag, check_etag
from application.rest_api.enums import AcceptHeader
from application.rest_api.rest_plus import api
from application.rest_api.vcf_files.schemas import VcfFilePaginationRequestSchema, VcfFilePaginationResponseSchema, \
    VcfFilePostRequestSchema, VcfFilePostResponseSchema, VcfFileDeleteRequestSchema, VcfFileDeletedResponseSchema, \
    VcfFileUpdateRequestSchema, VcfFileUpdateResponseSchema
from application.user.enums import Permission
from application.vcf_files.factories import vcf_file_pagination_service, append_data_to_vcf_file_service, \
    vcf_file_filter_out_by_id_service, vcf_file_update_by_id_service

ns = api.namespace(
    "vcf-files", description="VCF files related endpoints."
)


@ns.route("")
class VcfFilePagination(Resource):
    @accept(AcceptHeader.json.value, AcceptHeader.xml.value, AcceptHeader.all.value)
    @map_errors()
    @map_request(VcfFilePaginationRequestSchema())
    @check_etag()
    @add_etag(add_etag=True)
    @map_response(schema=VcfFilePaginationResponseSchema(), entity_name="results")
    def get(self, file_path: str, filter_id: str, page_size: int, page_index: int):
        """
        Controller for handling the VCF files pagination requests.

        :param file_path: The VCF filename.
        :param filter_id: The id to filter the VCF file with.
        :param page_size: The page size.
        :param page_index: The page index.

        :return: The paginated VCF File rows.
        """

        return vcf_file_pagination_service().apply(
            vcf_file_path=file_path,
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index,
        )


@ns.route("")
class AppendDataToVcfFile(Resource):
    @accept(AcceptHeader.json.value, AcceptHeader.xml.value, AcceptHeader.all.value)
    @map_errors()
    @guard(permission=Permission.execute)
    @map_request(VcfFilePostRequestSchema())
    @map_response(schema=VcfFilePostResponseSchema(), status_code=201)
    def post(self, file_path: str, data: List[Dict[str, Union[str, int]]]) -> Dict[str, Union[int, str]]:
        """
        Controller for handling appending rows to VCF files.

        :param file_path: The VCF filename.
        :param data: A list of rows to append to the file.

        :return: The total number of rows appended to the VCF file.
        """

        return append_data_to_vcf_file_service().apply(vcf_file_path=file_path, data=data)


@ns.route("")
class DeleteDataToVcfFile(Resource):
    @accept(AcceptHeader.json.value, AcceptHeader.xml.value, AcceptHeader.all.value)
    @map_errors()
    @guard(permission=Permission.execute)
    @map_request(VcfFileDeleteRequestSchema())
    @map_response(status_code=204)
    def delete(self, file_path: str, filter_id: str) -> None:
        """
        Controller for handling removing rows to VCF files.

        :param file_path: The VCF filename.
        :param filter_id: The id rows to remove from the VCF file.

        :return: Upon successfully deletion, a 204 NO CONTENT response is returned.
        """

        vcf_file_filter_out_by_id_service().apply(vcf_file_path=file_path, filter_id=filter_id)


@ns.route("")
class UpdateDataToVcfFile(Resource):
    @accept(AcceptHeader.json.value, AcceptHeader.xml.value, AcceptHeader.all.value)
    @map_errors()
    @guard(permission=Permission.execute)
    @map_request(VcfFileUpdateRequestSchema())
    @map_response(schema=VcfFileUpdateResponseSchema(), status_code=201)
    def patch(
            self,
            file_path: str,
            filter_id: str,
            data: Dict[str, Union[str, int]]
    ) -> Dict[str, Union[int, str]]:
        """
        Controller for handling removing rows to VCF files.

        :param file_path: The VCF filename.
        :param filter_id: The id rows to remove from the VCF file.
        :param data: The data to update file by id.

        :return: The total number of rows updated to the VCF file.
        """

        return vcf_file_update_by_id_service().apply(vcf_file_path=file_path, filter_id=filter_id, data=data)
