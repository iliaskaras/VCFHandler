import gzip
import io
import mimetypes
from collections import OrderedDict
from typing import List, Tuple, Union

from application.infrastructure.error.errors import InvalidArgumentError, MultipleVCFHandlerBaseError, ValidationError
from application.rest_api.vcf_files.enums import VCFHeader
from application.vcf_files.errors import VcfRowsByIdNotExistError, VcfDataAppendError, VcfDataDeleteError, \
    VcfDataUpdateError
from application.vcf_files.models import VcfRow
import pandas as pd
from application.infrastructure.celery.celery import celery_app


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
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The Filter ID is required.'))
        if not headers:
            errors.append(InvalidArgumentError('At least one VCF header is required.'))
        if page_size is None or page_size <= 0:
            errors.append(InvalidArgumentError('A page size above 0 is required.'))
        if page_index is None or page_index < 0:
            errors.append(InvalidArgumentError('A page index above or equal to zero is required.'))

        if errors.errors:
            raise errors

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
        try:
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
        except Exception as ex:
            raise ValidationError(str(ex))
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
            vcf_rows: List[VcfRow] = None
    ) -> int:
        """
        Loads and filters a VCF File based on the provided filtered id.

        :param vcf_file_path: The VCF file path to load.
        :param vcf_rows: The list of VcfRows to append.

        :return: The total number of appended data rows.

        :raise InvalidArgumentError: If there is an invalid argument.
                VcfDataAppendError: If was an error appending data to the VCF file.
        """
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not vcf_rows:
            errors.append(InvalidArgumentError('At least one row of data is required.'))

        if errors.errors:
            raise errors

        # The second item in the tuple indicates the guessed filetype.
        # In case of .gz file, the guessed filetype is gzip
        # In case of .vcf file, the guessed filetype is None
        file_type: Tuple[Union[None, str], str] = mimetypes.guess_type(vcf_file_path)

        rows_to_add: List[str] = []

        for vcf_row in vcf_rows:
            vcf_row_dict: dict = vcf_row.__dict__
            vcf_row_dict['1'] = vcf_row_dict.pop('chrom')
            vcf_row_dict['2'] = vcf_row_dict.pop('pos')
            vcf_row_dict['3'] = vcf_row_dict.pop('identifier')
            vcf_row_dict['4'] = vcf_row_dict.pop('ref')
            vcf_row_dict['5'] = vcf_row_dict.pop('alt')

            rows_to_add.append('\t'.join([str(value) for value in OrderedDict(vcf_row_dict).values()]) + '\n')

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

        return len(vcf_rows)


class FilterOutRowsById:

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
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The filter id is required.'))

        if errors.errors:
            raise errors

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


class AsyncFilterOutRowsById:

    @celery_app.task(bind=True)
    def run(
            self,
            vcf_file_path: str = None,
            filter_id: str = None,
    ) -> int:
        """
        Async version.
        Loads and filters a VCF File based on the provided filtered id.

        :param vcf_file_path: The VCF file path to load.
        :param filter_id: The filter id.

        :return: The list of filtered by ID VcfRows.

        :raise InvalidArgumentError: If there is an invalid argument.
               VcfDataDeleteError: If there was an error in the data deletion logic.
        """
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The filter id is required.'))

        if errors.errors:
            raise errors

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
            data: VcfRow = None
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
        errors: MultipleVCFHandlerBaseError = MultipleVCFHandlerBaseError()
        if not vcf_file_path:
            errors.append(InvalidArgumentError('The VCF file path is required.'))
        if not filter_id:
            errors.append(InvalidArgumentError('The filter id is required.'))
        if not data:
            errors.append(InvalidArgumentError('Data are required.'))

        if errors.errors:
            raise errors

        # The second item in the tuple indicates the guessed filetype.
        # In case of .gz file, the guessed filetype is gzip
        # In case of .vcf file, the guessed filetype is None
        file_type: Tuple[Union[None, str], str] = mimetypes.guess_type(vcf_file_path)
        total_updated_rows = 0

        vcf_row_dict: dict = data.__dict__

        vcf_row_dict['1'] = vcf_row_dict.pop('chrom')
        vcf_row_dict['2'] = vcf_row_dict.pop('pos')
        vcf_row_dict['3'] = vcf_row_dict.pop('identifier')
        vcf_row_dict['4'] = vcf_row_dict.pop('ref')
        vcf_row_dict['5'] = vcf_row_dict.pop('alt')

        row_to_append = '\t'.join([str(value) for value in OrderedDict(vcf_row_dict).values()]) + '\t'

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
            raise VcfDataUpdateError(str(ex))

        return total_updated_rows
