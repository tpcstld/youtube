import mock
import os
import unittest

import list_files

@mock.patch.object(os, 'getcwd')
@mock.patch.object(os, 'listdir')
@mock.patch.object(os.path, 'isfile')
class ListFilesTest(unittest.TestCase):

    def testSimple(self, m_isfile, m_listdir, m_getcwd):
        """Should be able to list files."""
        # Setup
        m_getcwd.return_value = 'test'
        m_listdir.return_value = ['one.txt', 'two', 'three.py']
        m_isfile.return_value = True
        expected = ['one.txt', 'two', 'three.py']

        # Run
        result = list_files.list_files()

        assert expected == result

    def testNotFile(self, m_isfile, m_listdir, m_getcwd):
        """Should not list files that are not files."""
        # Setup
        m_getcwd.return_value = 'test'
        m_listdir.return_value = ['one', 'two']
        m_isfile.side_effect = [True, False]
        expected = ['one']

        # Run
        result = list_files.list_files()

        assert expected == result

    def testNoFiles(self, m_isfile, m_listdir, m_getcwd):
        """Can handle lack of files to list."""
        # Setup
        m_getcwd.return_value = 'test'
        m_listdir.return_value = []
        m_isfile.return_value = True
        expected = []

        # Run
        result = list_files.list_files()

        assert expected == result

if __name__ == '__main__':
    unittest.main()
