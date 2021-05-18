import pytest
from typing import Optional

from marshmallow import ValidationError

from application.rest_api.vcf_files.schemas import PostVcfRowSchema
from application.vcf_files.operations import FilterVcfFile


class TestPostVcfRowSchema:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.filter_vcf_file = FilterVcfFile()

    @pytest.mark.parametrize('chrom, pos, identifier, ref, alt, error', [
        # when_chrom_does_not_start_with_chr
        (
                "1", 5000, "rs12", "T", "C",
                ValidationError({'CHROM': ['String does not match expected pattern.']})
        ),
        # when_chrom_start_with_chr_but_not_followed_by_number_between_1_to_22
        (
                "chr0", 5000, "rs12", "T", "C",
                ValidationError({'CHROM': ['String does not match expected pattern.']})
        ),
        # when_chrom_start_with_chr_but_not_followed_by_0
        (
                "chr0", 5000, "rs12", "T", "C",
                ValidationError({'CHROM': ['String does not match expected pattern.']})
        ),
        # when_chrom_start_with_chr_but_not_followed_by_X_Y_M
        (
                "chrx", 5000, "rs12", "T", "C",
                ValidationError({'CHROM': ['String does not match expected pattern.']})
        ),
        # when_chrom_start_with_chr_but_not_followed_by_X_Y_M
        (
                "chry", 5000, "rs12", "T", "C",
                ValidationError({'CHROM': ['String does not match expected pattern.']})
        ),
        # when_chrom_start_with_chr_but_not_followed_by_X_Y_M
        (
                "chrc", 5000, "rs12", "T", "C",
                ValidationError({'CHROM': ['String does not match expected pattern.']})
        ),
    ])
    def test_chrom_validation_errors(
            self,
            chrom: Optional[str],
            pos: Optional[int],
            identifier: Optional[str],
            ref: Optional[str],
            alt: Optional[str],
            error: ValidationError,
    ) -> None:
        schema: PostVcfRowSchema = PostVcfRowSchema()
        vcf_row = {
            "CHROM": chrom,
            "POS": pos,
            "ID": identifier,
            "REF": ref,
            "ALT": alt,
        }
        with pytest.raises(ValidationError) as ex:
            schema.load(data=vcf_row)
        assert ex.value.args == error.args

    @pytest.mark.parametrize('chrom, pos, identifier, ref, alt', [
        # when_chrom_starts_with_chr_and_followed_by_1
        (
                "chr1", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_2
        (
                "chr2", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_3
        (
                "chr3", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_4
        (
                "chr4", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_5
        (
                "chr5", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_6
        (
                "chr6", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_7
        (
                "chr7", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_8
        (
                "chr8", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_9
        (
                "chr9", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_10
        (
                "chr10", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_11
        (
                "chr11", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_12
        (
                "chr12", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_13
        (
                "chr13", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_14
        (
                "chr14", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_15
        (
                "chr15", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_16
        (
                "chr16", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_17
        (
                "chr17", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_18
        (
                "chr18", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_19
        (
                "chr19", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_20
        (
                "chr20", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_21
        (
                "chr21", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_22
        (
                "chr22", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_X
        (
                "chrX", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_Y
        (
                "chrY", 5000, "rs12", "T", "C",
        ),
        # when_chrom_starts_with_chr_and_followed_by_M
        (
                "chrM", 5000, "rs12", "T", "C",
        ),
    ])
    def test_correct_chrom_validation(
            self,
            chrom: Optional[str],
            pos: Optional[int],
            identifier: Optional[str],
            ref: Optional[str],
            alt: Optional[str],
    ) -> None:
        schema: PostVcfRowSchema = PostVcfRowSchema()
        vcf_row = {
            "CHROM": chrom,
            "POS": pos,
            "ID": identifier,
            "REF": ref,
            "ALT": alt,
        }
        schema.load(data=vcf_row)

    @pytest.mark.parametrize('chrom, pos, identifier, ref, alt', [
        # when_identifier_starts_with_rs_and_followed_by_integer
        (
                "chr1", 5000, "rs12", "T", "C",
        ),
    ])
    def test_correct_identifier_validation(
            self,
            chrom: Optional[str],
            pos: Optional[int],
            identifier: Optional[str],
            ref: Optional[str],
            alt: Optional[str],
    ) -> None:
        schema: PostVcfRowSchema = PostVcfRowSchema()
        vcf_row = {
            "CHROM": chrom,
            "POS": pos,
            "ID": identifier,
            "REF": ref,
            "ALT": alt,
        }
        schema.load(data=vcf_row)

    @pytest.mark.parametrize('chrom, pos, identifier, ref, alt, error', [
        # when_identifier_starts_with_rs_and_followed_by_char
        (
                "chr1", 5000, "rss12", "T", "C",
                ValidationError({'ID': ['String does not match expected pattern.']})
        ),
        # when_identifier_starts_with_rs_and_followed_by_int_but_ends_with_char
        (
                "chr1", 5000, "rs12a", "T", "C",
                ValidationError({'ID': ['String does not match expected pattern.']})
        ),
        # when_identifier_starts_with_rs_and_followed_by_int_end_by_int_but_have_string_between
        (
                "chr1", 5000, "rs1s2", "T", "C",
                ValidationError({'ID': ['String does not match expected pattern.']})
        ),
        # when_identifier_starts_with_rs_but_not_followed_by_int
        (
                "chr1", 5000, "rs", "T", "C",
                ValidationError({'ID': ['String does not match expected pattern.']})
        ),
    ])
    def test_identifier_validation_errors(
            self,
            chrom: Optional[str],
            pos: Optional[int],
            identifier: Optional[str],
            ref: Optional[str],
            alt: Optional[str],
            error: ValidationError,
    ) -> None:
        schema: PostVcfRowSchema = PostVcfRowSchema()
        vcf_row = {
            "CHROM": chrom,
            "POS": pos,
            "ID": identifier,
            "REF": ref,
            "ALT": alt,
        }
        with pytest.raises(ValidationError) as ex:
            schema.load(data=vcf_row)
        assert ex.value.args == error.args

    @pytest.mark.parametrize('chrom, pos, identifier, ref, alt', [
        # when_ref_and_alt_start_with_A
        (
                "chr1", 5000, "rs12", "A", "A",
        ),
        # when_ref_and_alt_start_with_C
        (
                "chr1", 5000, "rs12", "C", "C",
        ),
        # when_ref_and_alt_start_with_G
        (
                "chr1", 5000, "rs12", "G", "G",
        ),
        # when_ref_and_alt_start_with_T
        (
                "chr1", 5000, "rs12", "T", "T",
        ),
        # when_ref_and_alt_start_with_.
        (
                "chr1", 5000, "rs12", ".", ".",
        ),
        # when_ref_and_alt_start_with_AC
        (
                "chr1", 5000, "rs12", "AC", "AC",
        ),
        # when_ref_and_alt_start_with_AG
        (
                "chr1", 5000, "rs12", "AG", "AG",
        ),
        # when_ref_and_alt_start_with_AT
        (
                "chr1", 5000, "rs12", "AT", "AT",
        ),
        # when_ref_and_alt_start_with_A.
        (
                "chr1", 5000, "rs12", "A.", "A.",
        ),
        # when_ref_and_alt_start_with_ACG
        (
                "chr1", 5000, "rs12", "ACG", "ACG",
        ),
        # when_ref_and_alt_start_with_ACT
        (
                "chr1", 5000, "rs12", "ACT", "ACT",
        ),
        # when_ref_and_alt_start_with_AC.
        (
                "chr1", 5000, "rs12", "AC.", "AC.",
        ),
        # when_ref_and_alt_start_with_ACGT
        (
                "chr1", 5000, "rs12", "ACGT", "ACGT",
        ),
    ])
    def test_correct_pos_validation(
            self,
            chrom: Optional[str],
            pos: Optional[int],
            identifier: Optional[str],
            ref: Optional[str],
            alt: Optional[str],
    ) -> None:
        schema: PostVcfRowSchema = PostVcfRowSchema()
        vcf_row = {
            "CHROM": chrom,
            "POS": pos,
            "ID": identifier,
            "REF": ref,
            "ALT": alt,
        }
        schema.load(data=vcf_row)

    @pytest.mark.parametrize('chrom, pos, identifier, ref, alt', [
        (
                "chr1", 5000, "rs12", "T", "C",
        ),
    ])
    def test_correct_ref_alt_validation(
            self,
            chrom: Optional[str],
            pos: Optional[int],
            identifier: Optional[str],
            ref: Optional[str],
            alt: Optional[str],
    ) -> None:
        schema: PostVcfRowSchema = PostVcfRowSchema()
        vcf_row = {
            "CHROM": chrom,
            "POS": pos,
            "ID": identifier,
            "REF": ref,
            "ALT": alt,
        }
        schema.load(data=vcf_row)

    @pytest.mark.parametrize('chrom, pos, identifier, ref, alt, error', [
        # when_alt_ref_contains_char_other_than_the_correct_ones
        (
                "chr1", 5000, "rs12", "c", "c",
                ValidationError(
                    {
                        'REF': ['String does not match expected pattern.'],
                        'ALT': ['String does not match expected pattern.']
                    }
                )
        ),
        # when_alt_ref_starts_with_a_char_other_than_the_correct_ones_and_correct
        (
                "chr1", 5000, "rs12", "cA", "cA",
                ValidationError(
                    {
                        'REF': ['String does not match expected pattern.'],
                        'ALT': ['String does not match expected pattern.']
                    }
                )
        ),
        # when_alt_ref_starts_with_a_correct_char_but_ends_with_incorrect
        (
                "chr1", 5000, "rs12", "Ac", "Ac",
                ValidationError(
                    {
                        'REF': ['String does not match expected pattern.'],
                        'ALT': ['String does not match expected pattern.']
                    }
                )
        ),
        # when_alt_ref_starts_with_a_correct_char_followed_by_incorrect_end_with_correct
        (
                "chr1", 5000, "rs12", "AcT", "AcT",
                ValidationError(
                    {
                        'REF': ['String does not match expected pattern.'],
                        'ALT': ['String does not match expected pattern.']
                    }
                )
        ),
    ])
    def test_ref_alt_validation_errors(
            self,
            chrom: Optional[str],
            pos: Optional[int],
            identifier: Optional[str],
            ref: Optional[str],
            alt: Optional[str],
            error: ValidationError,
    ) -> None:
        schema: PostVcfRowSchema = PostVcfRowSchema()
        vcf_row = {
            "CHROM": chrom,
            "POS": pos,
            "ID": identifier,
            "REF": ref,
            "ALT": alt,
        }
        with pytest.raises(ValidationError) as ex:
            schema.load(data=vcf_row)
        assert ex.value.args == error.args
