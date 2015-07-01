import sys
import unittest
from worldengine.cli.main import main
from worldengine import __main__

class TestCommon(unittest.TestCase):

    def test__main__(self):
        assert __main__

    def test_options(self):
        backup_argv = sys.argv
        sys.argv = ["python", "--help"]
        self.assertRaises(SystemExit, main)

        sys.argv = backup_argv

    # TODO: fill in the rest of the options and their possibilities


if __name__ == '__main__':
    unittest.main()
