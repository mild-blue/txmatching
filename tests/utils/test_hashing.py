import unittest

from txmatching.utils.persistent_hash import (initialize_persistent_hash,
                                              update_persistent_hash)


class TestWeCanHasNonASCII(unittest.TestCase):
    update_persistent_hash(initialize_persistent_hash(), 'Δ')
