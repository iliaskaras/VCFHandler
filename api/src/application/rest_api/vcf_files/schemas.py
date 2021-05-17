import re

from marshmallow import fields, validate
from marshmallow.schema import BaseSchema, Schema


class PostVcfRowSchema(Schema):
    chrom = fields.Str(
        data_key='CHROM',
        required=True,
        validate=validate.Regexp(regex=re.compile("^chr((2[0-2]|1[0-9]|[1-9]|[XYM])$)"))
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
        validate=validate.Regexp(regex=re.compile("^([ACGT.]$)"))
    )
    alt = fields.Str(
        data_key='ALT',
        required=True,
        validate=validate.Regexp(regex=re.compile("^([ACGT.]$)"))
    )


class VcfFilePostRequestSchema(BaseSchema):
    file_path = fields.Str(required=True, data_key='filePath', default=None)
    data = fields.Nested(PostVcfRowSchema, many=True, data_key='data')


class VcfFilePostResponseSchema(BaseSchema):
    total_rows_added = fields.Int(data_key='totalRowsAdded', default=0)
    file_path = fields.Str(data_key='filePath', required=True)


class VcfFilePaginationRequestSchema(BaseSchema):
    file_path = fields.Str(required=True, data_key='filePath', default=None)
    filter_id = fields.Str(required=True, data_key='id', default=None)
    page_size = fields.Int(
        data_key='pageSize', missing=30, required=False, allow_none=False, validate=validate.Range(min=1), strict=True
    )
    page_index = fields.Int(
        data_key='pageIndex', missing=0, required=False, allow_none=False, validate=validate.Range(min=0), strict=True
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