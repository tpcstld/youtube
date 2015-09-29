import unittest

import get_cache_key

class CacheKeyTests(unittest.TestCase):

    def testSimple(self):
        """Should return a good cache key."""
        result = get_cache_key.get_cache_key('one', 'two')
        assert 'one::::two' == result

if __name__ == '__main__':
    unittest.main()
