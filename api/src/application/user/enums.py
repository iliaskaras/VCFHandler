from typing import List

from enum import Enum


class Permission(Enum):
    read = 'read'
    write = 'write'
    execute = 'execute'

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]
