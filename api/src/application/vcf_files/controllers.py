from flask_restplus import Resource
from flask_accept import accept
from application.rest_api.decorators import map_request, map_response, map_errors, add_etag, check_etag
from application.rest_api.enums import AcceptHeader
from application.rest_api.rest_plus import api
from application.rest_api.vcf_files.schemas import VcfFilePaginationRequestSchema, VcfFilePaginationResponseSchema
from application.vcf_files.factories import vcf_file_pagination_service

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

        :return: The Jwt that contains the access token.
        """

        result = vcf_file_pagination_service().apply(
            vcf_file_path=file_path,
            filter_id=filter_id,
            page_size=page_size,
            page_index=page_index,
        )
        return result
