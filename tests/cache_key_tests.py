import unittest

class CacheKeyTests(unittest.TestCase):

    def simple(self):
        """Should return a good cache key."""
        result = main_._get_cache_key('one', 'two')
        assert 'one::::two' == result

if __name__ == '__main__':
    unittest.main()
