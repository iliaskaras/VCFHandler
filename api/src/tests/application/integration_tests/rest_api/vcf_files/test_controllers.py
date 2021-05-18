import io
from typing import Optional, List

import pytest
from deepdiff import DeepDiff
from flask import Response
from flask.testing import FlaskClient
from lxml import etree


class TestVcfFileGetPagination:

    def test_get_vcf_files_return_403_when_auth_token_not_provided(self, client: FlaskClient) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors':
                [
                    {'message': 'Missing Authorization Header', 'errorType': 403}
                ],
            'errorCode': 403
        }

    def test_get_vcf_files_return_403_when_jwt_not_have_correct_permission(
            self,
            client: FlaskClient,
            access_token_read_permission: str,
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs1&filePath=test.vcf&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_read_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors': [
                {'message': 'Permission denied.', 'errorType': 'AuthorizationError'}
            ],
            'errorCode': 403
        }

    def test_get_vcf_files_pagination_with_json_accept_header_and_gz_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_gzip_file
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs1&filePath=test.vcf.gz&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert response.status == '200 OK'
        assert response.status_code == 200
        assert DeepDiff(
            response.json, {
                "data": {
                    "results": {
                        "id": "rs1",
                        "pageIndex": 0,
                        "pageSize": 2,
                        "rows": [
                            {
                                "alt": "G",
                                "chrom": "chr1",
                                "id": "rs1",
                                "pos": 1,
                                "ref": "T"
                            },
                            {
                                "alt": "G",
                                "chrom": "chr2",
                                "id": "rs1",
                                "pos": 2,
                                "ref": "T"
                            }
                        ],
                        "total": 2
                    }
                },
                "status": 200
            }
        ) == {}

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers
        assert 'ETag: "file_path=test.vcf.gz&filter_id=rs1&page_index=0&page_size=2"' in response_headers

    def test_get_vcf_files_pagination_with_xml_accept_header_and_unzipped_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs1&filePath=test.vcf&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert response.status == '200 OK'
        assert response.status_code == 200
        assert DeepDiff(
            response.json, {
                "data": {
                    "results": {
                        "id": "rs1",
                        "pageIndex": 0,
                        "pageSize": 2,
                        "rows": [
                            {
                                "alt": "G",
                                "chrom": "chr1",
                                "id": "rs1",
                                "pos": 1,
                                "ref": "T"
                            },
                            {
                                "alt": "G",
                                "chrom": "chr2",
                                "id": "rs1",
                                "pos": 2,
                                "ref": "T"
                            }
                        ],
                        "total": 2
                    }
                },
                "status": 200
            }
        ) == {}

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers
        assert 'ETag: "file_path=test.vcf&filter_id=rs1&page_index=0&page_size=2"' in response_headers

    def test_get_vcf_files_pagination_return_304_no_content_response_when_if_no_match_header_provided(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs1&filePath=test.vcf&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/xml',
                'Content-Type': 'application/json',
                'If-None-Match': '"file_path=test.vcf&filter_id=rs1&page_index=0&page_size=2"'
            }
        )

        assert response.status == '304 NOT MODIFIED'
        assert response.status_code == 304
        assert response.json is None

    def test_get_vcf_files_pagination_return_406_not_acceptable_response_when_unsupported_accept_header_provided(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs1&filePath=test.vcf&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/javascript',
                'Content-Type': 'application/json',
            }
        )

        assert response.status == '406 NOT ACCEPTABLE'
        assert response.status_code == 406
        assert response.json == {}

    def test_get_vcf_files_pagination_return_json_default_response_when_the_all_accept_header_provided(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs1&filePath=test.vcf&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': '*/*',
                'Content-Type': 'application/json',
            }
        )

        assert response.status == '200 OK'
        assert response.status_code == 200
        assert DeepDiff(
            response.json, {
                "data": {
                    "results": {
                        "id": "rs1",
                        "pageIndex": 0,
                        "pageSize": 2,
                        "rows": [
                            {
                                "alt": "G",
                                "chrom": "chr1",
                                "id": "rs1",
                                "pos": 1,
                                "ref": "T"
                            },
                            {
                                "alt": "G",
                                "chrom": "chr2",
                                "id": "rs1",
                                "pos": 2,
                                "ref": "T"
                            }
                        ],
                        "total": 2
                    }
                },
                "status": 200
            }
        ) == {}

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers
        assert 'ETag: "file_path=test.vcf&filter_id=rs1&page_index=0&page_size=2"' in response_headers

    def test_get_vcf_files_pagination_return_xml_response_when_the_xml_accept_header_provided(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs1&filePath=test.vcf&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/xml',
                'Content-Type': 'application/json',
            }
        )

        assert response.status == '200 OK'
        assert response.status_code == 200

        expected_string_io = io.StringIO(''.join(
            b'<?xml version="1.0" ?>\n<all>\n\t<status type="int">200</status>\n\t<data type="dict">\n\t\t<results ' \
            b'type="dict">\n\t\t\t<total type="int">2</total>\n\t\t\t<id type="str">rs1</id>\n\t\t\t<pageSize ' \
            b'type="int">2</pageSize>\n\t\t\t<pageIndex type="int">0</pageIndex>\n\t\t\t<rows ' \
            b'type="list">\n\t\t\t\t<item type="dict">\n\t\t\t\t\t<ref type="str">T</ref>\n\t\t\t\t\t<pos ' \
            b'type="int">1</pos>\n\t\t\t\t\t<id type="str">rs1</id>\n\t\t\t\t\t<chrom ' \
            b'type="str">chr1</chrom>\n\t\t\t\t\t<alt type="str">G</alt>\n\t\t\t\t</item>\n\t\t\t\t<item ' \
            b'type="dict">\n\t\t\t\t\t<ref type="str">T</ref>\n\t\t\t\t\t<pos type="int">2</pos>\n\t\t\t\t\t<id ' \
            b'type="str">rs1</id>\n\t\t\t\t\t<chrom type="str">chr2</chrom>\n\t\t\t\t\t<alt ' \
            b'type="str">G</alt>\n\t\t\t\t</item>\n\t\t\t</rows>\n\t\t</results>\n\t</data>\n</all>\n '.decode("utf-8"))
        )
        actual_string_io = io.StringIO(''.join(response.data.decode("utf-8")))

        expected_tree = etree.parse(expected_string_io)
        actual_tree = etree.parse(actual_string_io)

        assert set(expected_tree.getroot().itertext()) == set(actual_tree.getroot().itertext())
        response_headers: str = str(response.headers)

        assert 'Content-Type: application/xml' in response_headers
        assert 'ETag: "file_path=test.vcf&filter_id=rs1&page_index=0&page_size=2"' in response_headers

    def test_get_vcf_files_pagination_return_404_not_found_when_no_rows_found(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.get(
            '/api/v1/vcf-files?id=rs15&filePath=test.vcf&pageSize=2',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        )

        assert response.status == '404 NOT FOUND'
        assert response.status_code == 404

        expected_error = {
            "errors": [
                {
                    "message": "None rows found in VCF by the provided id:rs15",
                    "errorType": "VcfRowsByIdNotExistError"
                }
            ],
            "errorCode": 404
        }

        t = response.json
        assert DeepDiff(expected_error, t) == {}

        response_headers = str(response.headers)
        assert 'Content-Type: application/json' in response_headers

    @pytest.mark.parametrize('request_uri, expected_error_response, expected_json_response', [
        # when_file_path_is_none
        (
                '/api/v1/vcf-files?id=rs15&pageSize=2',
                b'{"errors": [{"message": "filePath: [\'Missing data for required field.\']", "errorType": '
                b'"Unprocessable Entity"}], "errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': "filePath: ['Missing data for required field.']",
                             'errorType': 'Unprocessable Entity'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_file_path_is_empty
        (
                '/api/v1/vcf-files?filePath=&id=rs15&pageSize=2',
                b'{"errors": [{"message": "The VCF file path is required.", "errorType": "InvalidArgumentError"}], '
                b'"errorCode": 400}\n',
                {
                    'errors': [
                        {'message': 'The VCF file path is required.', 'errorType': 'InvalidArgumentError'}
                    ],
                    'errorCode': 400
                }
        ),
        # when_id_is_none
        (
                '/api/v1/vcf-files?filePath=test&pageSize=2',
                b'{"errors": [{"message": "id: [\'Missing data for required field.\']", "errorType": "Unprocessable '
                b'Entity"}], "errorCode": 400}\n',
                {
                    'errors': [
                        {
                            'message': "id: ['Missing data for required field.']", 'errorType': 'Unprocessable Entity'}
                    ],
                    'errorCode': 400
                }
        ),
        # when_id_is_empty
        (
                '/api/v1/vcf-files?filePath=test&id=&pageSize=2',
                b'{"errors": [{"message": "id: [\'String does not match expected pattern.\']", "errorType":'
                b' "Unprocessable Entity"}], "errorCode": 400}\n',
                {
                    'errors': [
                        {
                            'message': "id: ['String does not match expected pattern.']",
                            'errorType': 'Unprocessable Entity'}
                    ],
                    'errorCode': 400
                }
        ),
        # when_page_size_is_less_than_1
        (
                '/api/v1/vcf-files?filePath=test&id=rs123&pageSize=0',
                b'{"errors": [{"message": "pageSize: [\'Must be greater than or equal to 1.\']", "errorType": '
                b'"Unprocessable Entity"}], "errorCode": 400}\n',
                {
                    'errors':
                        [
                            {
                                'message': "pageSize: ['Must be greater than or equal to 1.']",
                                'errorType': 'Unprocessable Entity'
                            }
                        ],
                    'errorCode': 400}
        ),
        # when_page_index_is_less_than_0
        (
                '/api/v1/vcf-files?filePath=test&id=rs123&pageSize=1&pageIndex=-1',
                b'{"errors": [{"message": "pageIndex: [\'Must be greater than or equal to 0.\']", "errorType": '
                b'"Unprocessable Entity"}], "errorCode": 400}\n',
                {
                    'errors': [
                        {
                            'message': "pageIndex: ['Must be greater than or equal to 0.']",
                            'errorType': 'Unprocessable Entity'
                        }
                    ],
                    'errorCode': 400
                }
        ),
    ])
    def test_get_vcf_files_marshmallow_request_body_validations(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file,
            request_uri: Optional[str],
            expected_error_response: Optional[bytes],
            expected_json_response: Optional[dict]
    ) -> None:
        response: Response = client.get(
            request_uri,
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        )

        assert response.status == '400 BAD REQUEST'
        assert response.status_code == 400
        assert response.data == expected_error_response
        assert DeepDiff(response.json, expected_json_response) == {}


class TestAppendDataToVcfFile:

    def test_append_data_to_vcf_file_require_auth_token(self, client: FlaskClient) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors':
                [
                    {'message': 'Missing Authorization Header', 'errorType': 403}
                ],
            'errorCode': 403
        }

    def test_append_data_to_vcf_file_return_403_when_jwt_not_have_correct_permission(
            self,
            client: FlaskClient,
            access_token_read_permission: str
    ) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_read_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf",
                "data": [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ]
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors': [
                {'message': 'Permission denied.', 'errorType': 'AuthorizationError'}
            ],
            'errorCode': 403
        }

    def test_append_data_to_vcf_file_when_user_provides_gz_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_gzip_file,
    ) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf.gz",
                "data": [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ]
            }
        )

        assert response.status == '201 CREATED'
        assert response.status_code == 201
        assert DeepDiff(
            response.json, {'data': {'filePath': 'test.vcf.gz', 'totalRowsAdded': 2}, 'status': 201}
        ) == {}

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers

    def test_append_data_to_vcf_file_with_xml_accept_header_and_unzipped_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/xml',
                'Content-Type': 'application/json'
            },
            json={
                "filePath": "test.vcf",
                "data": [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ]
            }
        )

        assert response.status == '201 CREATED'
        assert response.status_code == 201
        expected_string_io = io.StringIO(''.join(
            b'<?xml version="1.0" ?>\n<all>\n\t<status type="int">201</status>\n\t<data '
            b'type="dict">\n\t\t<totalRowsAdded type="int">2</totalRowsAdded>\n\t\t<filePath '
            b'type="str">test.vcf</filePath>\n\t</data>\n</all>\n'.decode("utf-8"))
        )
        actual_string_io = io.StringIO(''.join(response.data.decode("utf-8")))

        expected_tree = etree.parse(expected_string_io)
        actual_tree = etree.parse(actual_string_io)

        assert set(expected_tree.getroot().itertext()) == set(actual_tree.getroot().itertext())

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/xml' in response_headers

    def test_append_data_to_vcf_file_with_json_accept_header_and_unzipped_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json={
                "filePath": "test.vcf",
                "data": [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ]
            }
        )

        assert response.status == '201 CREATED'
        assert response.status_code == 201
        assert DeepDiff(
            response.json, {
                "data": {
                    "filePath": "test.vcf",
                    "totalRowsAdded": 2
                },
                "status": 201
            }
        ) == {}

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers

    def test_append_data_to_vcf_file_with_default_accept_header_and_unzipped_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': '*/*',
                'Content-Type': 'application/json'
            },
            json={
                "filePath": "test.vcf",
                "data": [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ]
            }
        )

        assert response.status == '201 CREATED'
        assert response.status_code == 201
        assert DeepDiff(
            response.json, {
                "data": {
                    "filePath": "test.vcf",
                    "totalRowsAdded": 2
                },
                "status": 201
            }
        ) == {}

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers

    def test_append_data_to_vcf_file_return_406_not_acceptable_response_when_unsupported_accept_header_provided(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/octet-stream',
                'Content-Type': 'application/json'
            },
            json={
                "filePath": "test.vcf",
                "data": [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ]
            }
        )

        assert response.status == '406 NOT ACCEPTABLE'
        assert response.status_code == 406
        assert response.json == {}

    @pytest.mark.parametrize('file_path, data, expected_error_response, expected_json_response', [
        # when_file_path_is_none
        (
                None,
                [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ],
                b'{"errors": [{"message": "filePath: [\'Field may not be null.\']", "errorType": "Unprocessable '
                b'Entity"}], "errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': "filePath: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_file_path_is_empty
        (
                '',
                [
                    {"CHROM": "chr12", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs12"},
                    {"CHROM": "chr21", "POS": 1001, "ALT": "T", "REF": "G", "ID": "rs12"}
                ],
                b'{"errors": [{"message": "The VCF file path is required.", "errorType": "InvalidArgumentError"}], '
                b'"errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': 'The VCF file path is required.', 'errorType': 'InvalidArgumentError'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_data_is_none
        (
                'test.vcf',
                None,
                b'{"errors": [{"message": "data: [\'Field may not be null.\']", "errorType": "Unprocessable '
                b'Entity"}], "errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': "data: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_data_is_empty
        (
                'test.vcf',
                [],
                b'{"errors": [{"message": "At least one row of data is required.", "errorType": '
                b'"InvalidArgumentError"}], "errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': 'At least one row of data is required.', 'errorType': 'InvalidArgumentError'}
                        ],
                    'errorCode': 400
                }
        ),
    ])
    def test_append_data_to_vcf_file_marshmallow_request_body_validations(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            file_path: Optional[str],
            data: Optional[List[dict]],
            expected_error_response: Optional[bytes],
            expected_json_response: Optional[dict]
    ) -> None:
        response: Response = client.post(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": file_path,
                "data": data
            }
        )

        assert response.status == '400 BAD REQUEST'
        assert response.status_code == 400
        assert response.data == expected_error_response
        assert DeepDiff(response.json, expected_json_response) == {}


class TestDeleteDataToVcfFile:

    def test_delete_data_to_vcf_file_require_auth_token(self, client: FlaskClient) -> None:
        response: Response = client.delete(
            '/api/v1/vcf-files',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors':
                [
                    {'message': 'Missing Authorization Header', 'errorType': 403}
                ],
            'errorCode': 403
        }

    def test_delete_data_to_vcf_file_return_403_when_jwt_not_have_correct_permission(
            self,
            client: FlaskClient,
            access_token_read_permission: str
    ) -> None:
        response: Response = client.delete(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_read_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf",
                "id": 'rs1'
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors': [
                {'message': 'Permission denied.', 'errorType': 'AuthorizationError'}
            ],
            'errorCode': 403
        }

    def test_delete_data_to_vcf_file_when_user_provides_gz_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_gzip_file,
    ) -> None:
        response: Response = client.delete(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf.gz",
                "id": 'rs1'
            }
        )

        assert response.status == '204 NO CONTENT'
        assert response.status_code == 204

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers

    def test_delete_data_to_vcf_file_with_xml_accept_header_and_unzipped_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.delete(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf",
                "id": 'rs1'
            }
        )

        assert response.status == '204 NO CONTENT'
        assert response.status_code == 204

        response_headers: str = str(response.headers)

        assert 'Content-Type: application/json' in response_headers

    def test_delete_data_to_vcf_file_return_406_not_acceptable_response_when_unsupported_accept_header_provided(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.delete(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/octet-stream',
                'Content-Type': 'application/json'
            },
            json={
                "filePath": "test.vcf",
                "id": 'rs1'
            }
        )

        assert response.status == '406 NOT ACCEPTABLE'
        assert response.status_code == 406
        assert response.json == {}

    @pytest.mark.parametrize('file_path, filter_id, expected_error_response, expected_json_response', [
        # when_file_path_is_none
        (
                None,
                'rs12',
                b'{"errors": [{"message": "filePath: [\'Field may not be null.\']", "errorType": "Unprocessable '
                b'Entity"}], "errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': "filePath: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_file_path_is_empty
        (
                '',
                'rs12',
                b'{"errors": [{"message": "The VCF file path is required.", "errorType": "InvalidArgumentError"}], '
                b'"errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': 'The VCF file path is required.', 'errorType': 'InvalidArgumentError'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_id_is_none
        (
                'test.vcf',
                None,
                b'{"errors": [{"message": "id: [\'Field may not be null.\']", "errorType": "Unprocessable Entity"}], '
                b'"errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': "id: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_id_is_empty
        (
                '',
                None,
                b'{"errors": [{"message": "id: [\'Field may not be null.\']", "errorType": "Unprocessable Entity"}], '
                b'"errorCode": 400}\n',
                {
                    'errors': [
                        {'message': "id: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                    ],
                    'errorCode': 400
                }
        ),
    ])
    def test_delete_data_to_vcf_file_marshmallow_request_body_validations(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            file_path: Optional[str],
            filter_id: Optional[str],
            expected_error_response: Optional[bytes],
            expected_json_response: Optional[dict]
    ) -> None:
        response: Response = client.delete(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": file_path,
                "id": filter_id
            }
        )

        assert response.status == '400 BAD REQUEST'
        assert response.status_code == 400
        assert response.data == expected_error_response
        assert DeepDiff(response.json, expected_json_response) == {}

class TestUpdateDataToVcfFile:

    def test_update_data_to_vcf_file_require_auth_token(self, client: FlaskClient) -> None:
        response: Response = client.patch(
            '/api/v1/vcf-files',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors':
                [
                    {'message': 'Missing Authorization Header', 'errorType': 403}
                ],
            'errorCode': 403
        }

    def test_update_data_to_vcf_file_return_403_when_jwt_not_have_correct_permission(
            self,
            client: FlaskClient,
            access_token_read_permission: str
    ) -> None:
        response: Response = client.patch(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_read_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf",
                "id": 'rs1'
            }
        )

        assert response.status == '403 FORBIDDEN'
        assert response.status_code == 403
        assert response.json == {
            'errors': [
                {'message': 'Permission denied.', 'errorType': 'AuthorizationError'}
            ],
            'errorCode': 403
        }

    def test_update_data_to_vcf_file_when_user_provides_gz_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_gzip_file,
    ) -> None:
        response: Response = client.patch(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf.gz",
                "id": 'rs1',
                "data": {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
            }
        )

        assert response.status == '200 OK'
        assert response.status_code == 200

        response_headers: str = str(response.headers)
        assert DeepDiff(
            response.json, {'data': {'filePath': 'test.vcf.gz', 'totalRowsUpdated': 2}, 'status': 200}
        ) == {}
        assert 'Content-Type: application/json' in response_headers

    def test_update_data_to_vcf_file_with_xml_accept_header_and_unzipped_file(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.patch(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/xml',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": "test.vcf",
                "id": 'rs1',
                "data": {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
            }
        )

        assert response.status == '200 OK'
        assert response.status_code == 200

        response_headers: str = str(response.headers)
        expected_string_io = io.StringIO(''.join(
            b'<?xml version="1.0" ?>\n<all>\n\t<status type="int">200</status>\n\t<data '
            b'type="dict">\n\t\t<totalRowsUpdated type="int">2</totalRowsUpdated>\n\t\t<filePath '
            b'type="str">test.vcf</filePath>\n\t</data>\n</all>\n'.decode("utf-8"))
        )
        actual_string_io = io.StringIO(''.join(response.data.decode("utf-8")))

        expected_tree = etree.parse(expected_string_io)
        actual_tree = etree.parse(actual_string_io)

        assert set(expected_tree.getroot().itertext()) == set(actual_tree.getroot().itertext())

        assert 'Content-Type: application/xml' in response_headers

    def test_update_data_to_vcf_file_return_406_not_acceptable_response_when_unsupported_accept_header_provided(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.patch(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/octet-stream',
                'Content-Type': 'application/json'
            },
            json={
                "filePath": "test.vcf",
                "id": 'rs1',
                "data": {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
            }
        )

        assert response.status == '406 NOT ACCEPTABLE'
        assert response.status_code == 406
        assert response.json == {}

    def test_update_data_to_vcf_file_return_404_when_no_rows_found_to_update(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            setup_vcf_unzipped_file
    ) -> None:
        response: Response = client.patch(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json={
                "filePath": "test.vcf",
                "id": 'rs15',
                "data": {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
            }
        )

        expected_json_response = {
            'errors':
                [
                    {'message': 'No data found for update', 'errorType': 'VcfDataUpdateError'}
                ],
            'errorCode': 404
        }
        assert response.status == '404 NOT FOUND'
        assert response.status_code == 404
        assert DeepDiff(response.json, expected_json_response) == {}

    @pytest.mark.parametrize('file_path, filter_id, data, expected_error_response, expected_json_response', [
        # when_file_path_is_none
        (
                None,
                'rs12',
                {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
                b'{"errors": [{"message": "filePath: [\'Field may not be null.\']", "errorType": "Unprocessable '
                b'Entity"}], "errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': "filePath: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_file_path_is_empty
        (
                '',
                'rs12',
                {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
                b'{"errors": [{"message": "The VCF file path is required.", "errorType": "InvalidArgumentError"}], '
                b'"errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': 'The VCF file path is required.', 'errorType': 'InvalidArgumentError'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_id_is_none
        (
                'test.vcf',
                None,
                {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
                b'{"errors": [{"message": "id: [\'Field may not be null.\']", "errorType": "Unprocessable Entity"}], '
                b'"errorCode": 400}\n',
                {
                    'errors':
                        [
                            {'message': "id: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                        ],
                    'errorCode': 400
                }
        ),
        # when_id_is_empty
        (
                '',
                None,
                {"CHROM": "chr13", "POS": 1000, "ALT": "T", "REF": "AGCT", "ID": "rs1"},
                b'{"errors": [{"message": "id: [\'Field may not be null.\']", "errorType": "Unprocessable Entity"}], '
                b'"errorCode": 400}\n',
                {
                    'errors': [
                        {'message': "id: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                    ],
                    'errorCode': 400
                }
        ),
        # when_data_is_none
        (
                'test.vcf',
                'rs12',
                None,
                b'{"errors": [{"message": "data: [\'Field may not be null.\']", "errorType": "Unprocessable Entity"}], '
                b'"errorCode": 400}\n',
                {
                    'errors': [
                        {'message': "data: ['Field may not be null.']", 'errorType': 'Unprocessable Entity'}
                    ],
                    'errorCode': 400
                }
        ),
    ])
    def test_update_data_to_vcf_file_marshmallow_request_body_validations(
            self,
            client: FlaskClient,
            access_token_execute_permission: str,
            file_path: Optional[str],
            filter_id: Optional[str],
            data: Optional[dict],
            expected_error_response: Optional[bytes],
            expected_json_response: Optional[dict]
    ) -> None:
        response: Response = client.patch(
            '/api/v1/vcf-files',
            headers={
                'Authorization': f'Bearer {access_token_execute_permission}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={
                "filePath": file_path,
                "id": filter_id,
                "data": data
            }
        )

        assert response.status == '400 BAD REQUEST'
        assert response.status_code == 400
        assert response.data == expected_error_response
        assert DeepDiff(response.json, expected_json_response) == {}
