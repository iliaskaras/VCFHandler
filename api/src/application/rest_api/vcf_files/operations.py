import gzip
import io
import mimetypes
from typing import List, Tuple, Union

from application.infrastructure.error.errors import InvalidArgumentError
from application.rest_api.vcf_files.enums import VCFHeader
from application.vcf_files.errors import VcfRowsByIdNotExistError
from application.vcf_files.models import VcfRow
import pandas as pd


class FilterVcfFile:

    def run(
            self,
            vcf_file_path: str = None,
            headers: List[VCFHeader] = None,
            filter_id: str = None,
            page_size: int = 10,
            page_index: int = 0,
    ) -> List[VcfRow]:
        """
        Loads and filters a VCF File based on the provided filtered id.

        @:param vcf_file_path: The VCF file path to load.
        @:param headers: The VCF file headers to load.
        @:param filter_id: The source node.
        @:param page_size: The size of the page.
        @:param page_index: The index of the page.

        @:return: The list of filtered by ID VcfRows.

        @:raise InvalidArgumentError: If there is an invalid argument.
                VcfRowsByIdNotExistError: If there aren't any rows filtered by the provided filter id.
        """
        if not vcf_file_path:
            raise InvalidArgumentError('The VCF file path is required.')
        if not headers:
            raise InvalidArgumentError('At least one VCF header is required.')
        if page_size <= 0:
            raise InvalidArgumentError('The page size is required.')
        if page_index < 0:
            raise InvalidArgumentError('The page index is required.')

        # The second item in the tuple indicates the guessed filetype.
        # In case of .gz file, the guessed filetype is gzip
        # In case of .vcf file, the guessed filetype is None
        file_type: Tuple[Union[None, str], str] = mimetypes.guess_type(vcf_file_path)

        if file_type[1] == 'gzip':
            with gzip.open(vcf_file_path, 'r') as file:
                rows = [row.decode("utf-8") for row in file if not row.startswith(b'##')]
        elif file_type[1] is None:
            with open(vcf_file_path, 'r') as file:
                rows = [row for row in file if not row.startswith('##')]

        # Use io.StringIO because we do not have the an actual csv file.
        # Read as csv the rows, keep the columns that we are interested in and rename them to map them later on.
        # Query the csv by the ID column (renamed to identifier).
        df_rows = pd.read_csv(
            io.StringIO(''.join(rows)),
            sep='\t',
            usecols=[header.value for header in headers],
            dtype={'POS': int},
        ).rename(
            columns={
                '#CHROM': 'chrom',
                'POS': 'pos',
                'ID': 'identifier',
                'REF': 'ref',
                'ALT': 'alt',
            }
        ).query('identifier == \'{0}\''.format(filter_id))

        # Keep the page rows only.
        _from = page_index * page_size
        paginated_df_rows = df_rows[_from:][:page_size]

        # Map the found df rows to our VcfRow model.
        vcf_rows: List[VcfRow] = [
            VcfRow(
                **dict(paginated_row)
            )
            for index, paginated_row in paginated_df_rows.iterrows()
        ]

        if not vcf_rows:
            raise VcfRowsByIdNotExistError('None rows found in VCF by the provided id:{}'.format(filter_id))

        return vcf_rows
