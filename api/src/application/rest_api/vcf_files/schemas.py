from marshmallow import fields, validate
from marshmallow.schema import BaseSchema, Schema


class VcfFilePaginationRequestSchema(BaseSchema):
    file_path = fields.Str(required=True, data_key='filePath', default=None)
    filter_id = fields.Str(required=True, data_key='id', default=None)
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