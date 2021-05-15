from enum import Enum
from typing import List


class Environment(Enum):
    local = "local"
    test = "test"
    production = "production"

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]
