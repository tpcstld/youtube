import unittest

from .. import main

class CacheKeyTests(unittest.TestCase):

    def testSimple(self):
        """Should return a good cache key."""
        result = main._get_cache_key('one', 'two')
        assert 'one::::two' == result

if __name__ == '__main__':
    unittest.main()
