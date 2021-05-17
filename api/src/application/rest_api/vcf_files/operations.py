import gzip
import io
import mimetypes
from collections import OrderedDict
from typing import List, Tuple, Union, Dict

from application.infrastructure.error.errors import InvalidArgumentError
from application.rest_api.vcf_files.enums import VCFHeader
from application.vcf_files.errors import VcfRowsByIdNotExistError, VcfDataAppendError, VcfDataDeleteError
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

        :param vcf_file_path: The VCF file path to load.
        :param headers: The VCF file headers to load.
        :param filter_id: The filter id.
        :param page_size: The size of the page.
        :param page_index: The index of the page.

        :return: The list of filtered by ID VcfRows.

        :raise InvalidArgumentError: If there is an invalid argument.
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


class AppendToVcfFile:

    def run(
            self,
            vcf_file_path: str = None,
            data: List[Dict[str, Union[str, int]]] = None
    ) -> int:
        """
        Loads and filters a VCF File based on the provided filtered id.

        :param vcf_file_path: The VCF file path to load.
        :param data: The list of data to append.

        :return: The total number of appended data rows.

        :raise InvalidArgumentError: If there is an invalid argument.
                VcfDataAppendError: If was an error appending data to the VCF file.
        """
        if not vcf_file_path:
            raise InvalidArgumentError('The VCF file path is required.')
        if not data:
            raise InvalidArgumentError('At least one row of data is required.')

        # The second item in the tuple indicates the guessed filetype.
        # In case of .gz file, the guessed filetype is gzip
        # In case of .vcf file, the guessed filetype is None
        file_type: Tuple[Union[None, str], str] = mimetypes.guess_type(vcf_file_path)

        rows_to_add: List[str] = []

        for _data in data:
            _data['1'] = _data.pop('chrom')
            _data['2'] = _data.pop('pos')
            _data['3'] = _data.pop('identifier')
            _data['4'] = _data.pop('ref')
            _data['5'] = _data.pop('alt')

            rows_to_add.append('\t'.join([str(value) for value in OrderedDict(_data).values()]) + '\n')

        try:
            if file_type[1] == 'gzip':
                with gzip.open(vcf_file_path, 'a') as file:
                    for row in rows_to_add:
                        file.write(str.encode(row))
            elif file_type[1] is None:
                with open(vcf_file_path, 'a') as file:
                    for row in rows_to_add:
                        file.write(row)
        except Exception as ex:
            raise VcfDataAppendError(str(ex))

        return len(data)


class FilterOutByIdVcfFile:

    def run(
            self,
            vcf_file_path: str = None,
            filter_id: str = None,
    ) -> int:
        """
        Loads and filters a VCF File based on the provided filtered id.

        :param vcf_file_path: The VCF file path to load.
        :param filter_id: The filter id.

        :return: The list of filtered by ID VcfRows.

        :raise InvalidArgumentError: If there is an invalid argument.
               VcfDataDeleteError: If there was an error in the data deletion logic.
        """
        if not vcf_file_path:
            raise InvalidArgumentError('The VCF file path is required.')
        if not filter_id:
            raise InvalidArgumentError('The filter id is required.')

        # The second item in the tuple indicates the guessed filetype.
        # In case of .gz file, the guessed filetype is gzip
        # In case of .vcf file, the guessed filetype is None
        file_type: Tuple[Union[None, str], str] = mimetypes.guess_type(vcf_file_path)
        total_deleted_rows = 0

        try:

            if file_type[1] == 'gzip':
                with gzip.open(vcf_file_path, 'r') as file:
                    rows = []
                    for row in file:
                        if row.startswith(b'##') or row.startswith(b'#'):
                            rows.append(row)
                            continue
                        row_id = row.split(b'\t')[2].decode("utf-8")
                        if row_id != filter_id:
                            rows.append(row)
                        else:
                            total_deleted_rows += 1

                with gzip.open(vcf_file_path, 'wb') as file:
                    file.writelines(rows)

            elif file_type[1] is None:
                with open(vcf_file_path, 'r') as file:
                    rows = []
                    for row in file:
                        if row.startswith('##') or row.startswith('#'):
                            rows.append(row)
                            continue
                        row_id = row.split('\t')[2]
                        if row_id != filter_id:
                            rows.append(row)
                        else:
                            total_deleted_rows += 1

                with open(vcf_file_path, 'w') as file:
                    file.writelines(rows)
        except Exception as ex:
            raise VcfDataDeleteError(str(ex))

        return total_deleted_rows


class UpdateByIdVcfFile:

    def run(
            self,
            vcf_file_path: str = None,
            filter_id: str = None,
            data: Dict[str, Union[str, int]] = None
    ) -> int:
        """
        Loads and updates a VCF File based on the provided filtered id.

        :param vcf_file_path: The VCF file path to load.
        :param filter_id: The filter id.
        :param data: The data to update file by id.

        :return: The list of filtered by ID VcfRows.

        :raise InvalidArgumentError: If there is an invalid argument.
               VcfDataDeleteError: If there was an error in the data deletion logic.
        """
        if not vcf_file_path:
            raise InvalidArgumentError('The VCF file path is required.')
        if not filter_id:
            raise InvalidArgumentError('The filter id is required.')
        if not data:
            raise InvalidArgumentError('Data are required.')

        # The second item in the tuple indicates the guessed filetype.
        # In case of .gz file, the guessed filetype is gzip
        # In case of .vcf file, the guessed filetype is None
        file_type: Tuple[Union[None, str], str] = mimetypes.guess_type(vcf_file_path)
        total_updated_rows = 0

        data['1'] = data.pop('chrom')
        data['2'] = data.pop('pos')
        data['3'] = data.pop('identifier')
        data['4'] = data.pop('ref')
        data['5'] = data.pop('alt')

        row_to_append = '\t'.join([str(value) for value in OrderedDict(data).values()])+'\t'

        try:

            if file_type[1] == 'gzip':
                with gzip.open(vcf_file_path, 'r') as file:
                    rows = []
                    for row in file:
                        if row.startswith(b'##') or row.startswith(b'#'):
                            rows.append(row)
                            continue
                        row_id = row.split(b'\t')[2].decode("utf-8")
                        if row_id != filter_id:
                            rows.append(row)
                        else:
                            columns_to_not_update: bytes = b'\t'.join(row.split(b'\t')[5:])
                            final_updated_row: bytes = str.encode(row_to_append) + columns_to_not_update
                            rows.append(final_updated_row)
                            total_updated_rows += 1

                with gzip.open(vcf_file_path, 'wb') as file:
                    file.writelines(rows)

            elif file_type[1] is None:
                with open(vcf_file_path, 'r') as file:
                    rows = []
                    for row in file:
                        if row.startswith('##') or row.startswith('#'):
                            rows.append(row)
                            continue
                        row_id = row.split('\t')[2]
                        if row_id != filter_id:
                            rows.append(row)
                        else:
                            columns_to_not_update: str = '\t'.join(row.split('\t')[5:])
                            final_updated_row: str = row_to_append + columns_to_not_update
                            rows.append(final_updated_row)
                            total_updated_rows += 1

                with open(vcf_file_path, 'w') as file:
                    file.writelines(rows)
        except Exception as ex:
            raise VcfDataDeleteError(str(ex))

        return total_updated_rows
