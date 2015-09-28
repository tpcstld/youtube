import mock
import unittest

from .. import main

@mock.patch.object(main.list_files, 'list_files')
class ListFilesTest(unittest.TestCase):

    def testSimple(self, m_list_files):
        """Should be able to return files listed."""
        # Setup
        m_list_files.return_value = ['one', 'two', 'three']
        expected = 'one\ntwo\nthree'

        # Setup
        result = main.list_files_route()
        assert expected == result

    def testNoFiles(self, m_list_files):
        """Should be able to return something when there's no files."""
        # Setup
        m_list_files.return_value = []
        expected = 'There are no files.'

        # Setup
        result = main.list_files_route()
        assert expected == result

if __name__ == '__main__':
    unittest.main()
