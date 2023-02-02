import unittest

from tests.test_utilities.create_dataclasses import (get_test_donors,
                                                     get_test_recipients)
from tests.test_utilities.hla_preparation_utils import create_hla_type
from txmatching.utils.persistent_hash import (initialize_persistent_hash,
                                              update_persistent_hash)


class TestPersistentHash(unittest.TestCase):

    def _assert_hash(self, value, expected_hash_digest):
        hash_ = initialize_persistent_hash()
        update_persistent_hash(hash_, value)
        self.assertEqual(expected_hash_digest, hash_.hexdigest())

    def test_hashing(self):
        self._assert_hash('foo', '56c527b4cc0b522b127062dec3201194')
        self._assert_hash('42', 'aa0a056d9e7d1b3b17530b46107b91a3')
        self._assert_hash(42, 'd1e2cf72d8bf073f0bc2d0e8794b31ae')
        self._assert_hash(42.0, 'ee8b51ea1d5859dc45035c4ee9fcaedc')
        self._assert_hash(True, '3b3e200b7cda75063ec203db706d2463')
        self._assert_hash([42], '7c4aa0d7ffabc559d31ae902ae2b93a6')
        self._assert_hash([1, 2], '50d69227171683e044fc85f530d31568')
        with self.assertRaises(NotImplementedError):
            self._assert_hash({1, 2}, '26b3a59f9692f43f20db24e6ab242cb7')
        self._assert_hash((1, True), 'e70e4791e78da2db05688c6043a20d86')
        with self.assertRaises(NotImplementedError):
            self._assert_hash({'a': 'b'}, 'e4625008dde72175d331df31f62572e9')
        self._assert_hash(None, '6af5817033462a81dfdff478e27e824d')
        self._assert_hash(create_hla_type('A9'), 'b81f11cc22faf6f2dc6259676d9c87ed')
        self._assert_hash(get_test_donors(), '8abd6f9b74db69e60cf086d292d5aefa')
        self._assert_hash(get_test_recipients(), 'c670c716a9752c22148cf5ba06485305')

    def test_functions_update_persistent_hash(self):
        value = create_hla_type('A9')
        hash_1 = initialize_persistent_hash()
        update_persistent_hash(hash_1, value)
        hash_2 = initialize_persistent_hash()
        value.update_persistent_hash(hash_2)
        self.assertEqual(hash_1.hexdigest(), hash_2.hexdigest())
