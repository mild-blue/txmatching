from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime

# pylint: disable=undefined-variable
HashType: TypeAlias = 'hashlib._Hash'


class PersistentlyHashable(ABC):
    @abstractmethod
    def update_persistent_hash(self, hash_: HashType):
        pass

    def persistent_hash(self):
        hash_ = initialize_persistent_hash()
        self.update_persistent_hash(hash_)
        return get_hash_digest(hash_)


def initialize_persistent_hash() -> HashType:
    return hashlib.md5()


def get_hash_digest(hash_: HashType) -> int:
    # Decrease hash size so that it would fit to postgres BIGINT (INT8)
    return int(hash_.hexdigest(), 16) % 2**63


def update_persistent_hash(hash_: HashType, value: any):
    """
    Create hash for a given value that is persistent across app sessions. Contrary to this function, a hash created
    using `hash()` function is not persistent (see https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHASHSEED)
    """

    if isinstance(value, type):
        hash_.update(f'__{value.__name__}__'.encode('ASCII'))
    elif isinstance(value, PersistentlyHashable):
        value.update_persistent_hash(hash_)
    else:
        update_persistent_hash(hash_, type(value))

        # Note: Creating hash of set or dict using this way would be possibly not secure
        #       (see: https://stackoverflow.com/questions/15479928)
        #       One option for implementing that is to sort the values or keys by their persistent hash
        if isinstance(value, str):
            hash_.update(value.encode('ASCII'))
        elif isinstance(value, (int, bool, float, datetime)):
            update_persistent_hash(hash_, str(value))
        elif isinstance(value, (list, tuple)):
            for item in value:
                update_persistent_hash(hash_, item)
        elif value is None:
            update_persistent_hash(hash_, '__none__')
        else:
            raise NotImplementedError(f'Hashing type {type(value)} ({value}) not implemented')
