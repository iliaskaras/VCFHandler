import re

from marshmallow import fields, validate, post_load
from marshmallow.schema import BaseSchema, Schema

from application.vcf_files.models import VcfRow


# Validations on the fields are based on what the provided real file contains.
# ref & alt: contains any number of ACGT. char occurrences.
# chrom: contains a string starts with chr, followed by a number from 1 to 22 or followed by a X, Y or M.
class PostVcfRowSchema(Schema):
    chrom = fields.Str(
        data_key='CHROM',
        required=True,
        validate=validate.Regexp(regex=re.compile("^chr((2[0-2]|1[0-9]|[1-9]|([X]?|[Y]?|[M])?)$)"))
    )
    pos = fields.Int(data_key='POS', required=True, strict=True)
    identifier = fields.Str(
        data_key='ID',
        required=True,
        validate=validate.Regexp(regex=re.compile("^rs([0-9]+$)"))
    )
    ref = fields.Str(
        data_key='REF',
        required=True,
        validate=validate.Regexp(regex=re.compile("([ACGT.]*)$"))
    )
    alt = fields.Str(
        data_key='ALT',
        required=True,
        validate=validate.Regexp(regex=re.compile("([ACGT.]*)$"))
    )

    @post_load
    def load_vcf_row(self, data, **kwargs):
        if isinstance(data, dict):
            return VcfRow(**data)
        else:
            return data


class VcfFilePostRequestSchema(BaseSchema):
    file_path = fields.Str(required=True, data_key='filePath', default=None)
    data = fields.Nested(PostVcfRowSchema, many=True, data_key='data', required=True)


class VcfFileFilteringRequestSchema(BaseSchema):
    file_path = fields.Str(required=True, data_key='filePath', default=None)
    filter_id = fields.Str(
        required=True,
        data_key='id',
        default=None,
        validate=validate.Regexp(regex=re.compile("^rs([0-9]+$)"))
    )


class VcfFileDeleteRequestSchema(VcfFileFilteringRequestSchema):
    filter_id = fields.Str(
        required=True,
        data_key='id',
        default=None,
        validate=validate.Regexp(regex=re.compile("^rs([0-9]+$)"))
    )
    file_path = fields.Str(required=True, data_key='filePath', default=None)


class VcfFileUpdateRequestSchema(VcfFileFilteringRequestSchema):
    filter_id = fields.Str(
        required=True,
        data_key='id',
        default=None,
        validate=validate.Regexp(regex=re.compile("^rs([0-9]+$)"))
    )
    file_path = fields.Str(required=True, data_key='filePath', default=None)
    data = fields.Nested(PostVcfRowSchema, data_key='data', required=True)


class VcfFileDeletedResponseSchema(BaseSchema):
    total_rows_deleted = fields.Int(data_key='totalRowsDeleted', default=0)
    file_path = fields.Str(data_key='filePath', required=True)


class VcfFileUpdateResponseSchema(BaseSchema):
    total_rows_updated = fields.Int(data_key='totalRowsUpdated', default=0)
    file_path = fields.Str(data_key='filePath', required=True)


class VcfFilePostResponseSchema(BaseSchema):
    total_rows_added = fields.Int(data_key='totalRowsAdded', default=0)
    file_path = fields.Str(data_key='filePath', required=True)


class VcfFilePaginationRequestSchema(BaseSchema):
    file_path = fields.Str(required=True, data_key='filePath', default=None)
    filter_id = fields.Str(
        required=True, data_key='id', default=None,  validate=validate.Regexp(regex=re.compile("^rs([0-9]+$)"))
    )
    page_size = fields.Int(
        data_key='pageSize', missing=30, required=False, allow_none=False, validate=validate.Range(min=1)
    )
    page_index = fields.Int(
        data_key='pageIndex', missing=0, required=False, allow_none=False, validate=validate.Range(min=0)
    )


class VcfRowSchema(Schema):
    chrom = fields.Str(data_key='chrom')
    pos = fields.Int(data_key='pos')
    identifier = fields.Str(data_key='id')
    ref = fields.Str(data_key='ref')
    alt = fields.Str(data_key='alt')


class VcfFilePaginationResponseSchema(BaseSchema):
    results = fields.Nested(VcfRowSchema, many=True, data_key='rows')
    page_size = fields.Int(data_key='pageSize')
    page_index = fields.Int(data_key='pageIndex')
    total = fields.Int(data_key='total')
    filtered_id = fields.Str(data_key='id')
