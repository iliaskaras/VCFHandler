from typing import List

from enum import Enum


class VCFHeader(Enum):
    chrom = '#CHROM'
    pos = 'POS'
    alt = 'ALT'
    ref = 'REF'
    id = 'ID'

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]
