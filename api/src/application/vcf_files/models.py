from typing import List

from attr import attrs, attrib


@attrs(auto_attribs=True)
class VcfRow:
    chrom: str = None
    pos: int = None
    identifier: str = None
    ref: str = None
    alt: str = None


@attrs
class FilteredVcfRowsPage:
    results = attrib(type=List[VcfRow])
    total = attrib(type=int)
    filtered_id = attrib(type=str)
    page_size = attrib(type=int)
    page_index = attrib(type=int)


@attrs
class AppendRowsExecutionArtifact:
    file_path = attrib(type=str)
    total_rows_added = attrib(type=int)


@attrs
class UpdatedRowsExecutionArtifact:
    file_path = attrib(type=str)
    total_rows_updated = attrib(type=int)
