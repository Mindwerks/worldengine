import os
import sys
from tests.draw_test import TestBase
import unittest
from worldengine import __main__
from worldengine.cli.main import main


class TestCLI(TestBase):

    def setUp(self):
        super(TestCLI, self).setUp()
        self.world = "%s/seed_28070.world" % self.tests_data_dir

    def test__main__(self):
        assert __main__

    def test_options(self):
        backup_argv = sys.argv
        sys.argv = ["python", "--help"]
        self.assertRaises(SystemExit, main)
        sys.argv = ["python", "--version"]
        self.assertRaises(SystemExit, main)
        sys.argv = ["python", "info"]
        self.assertRaises(SystemExit, main)
        sys.argv = ["python", "infooooooooo"]
        self.assertRaises(SystemExit, main)
        sys.argv = ["python", "info", "does_not_exist"]
        self.assertRaises(SystemExit, main)
        sys.argv = ["python", "info", "--gs"]
        self.assertRaises(SystemExit, main)
        sys.argv = ["python", "-o", __file__]
        self.assertRaises(Exception, main)
        sys.argv = ["python", "info", "-o", "test_dir"]
        self.assertRaises(SystemExit, main)
        self.assertTrue(os.path.isdir("test_dir"))
        sys.argv = ["python", "plates", "--number-of-plates", "0"]
        self.assertRaises(SystemExit, main)
        sys.argv = ["python", "plates", "--number-of-plates", "101"]
        self.assertRaises(SystemExit, main)

    def test_warnings(self):
        backup_argv = sys.argv
        sys.argv = ["python", "--width", "16", "--height", "16",
                    "--temps", "1.1/.235/.406/.561/.634/-.1", "--humidity",
                    "1.1/.222/.493/.764/.927/.986/-.1"]
        try:
            main()
        except Exception as e:
            raise e

    def test_smoke_info(self):
        backup_argv = sys.argv
        sys.argv = ["python", "info", self.world]
        try:
            main()
        except Exception as e:
            raise e
        # TODO: fill in the rest of the options and their possibilities
        sys.argv = backup_argv

    def test_smoke_full(self):
        # the big smoke test, can we go through
        # everything without it exploding?
        backup_argv = sys.argv
        sys.argv = ["python", "--width", "16", "--height", "16",
                    "-r", "-v", "--gs", "--scatter", "--temps",
                    ".126/.235/.406/.561/.634/.876", "--humidity",
                    ".059/.222/.493/.764/.927/.986/.998", "-go", ".2",
                    "-gv", "1.25"]
        try:
            main()
        except Exception as e:
            raise e

    def test_smoke_ancient(self):
            backup_argv = sys.argv
            sys.argv = ["python", "ancient_map", "-w", self.world]
            try:
                main()
            except Exception as e:
                raise e
            sys.argv = backup_argv

    def test_smoke_plates(self):
            backup_argv = sys.argv
            sys.argv = ["python", "plates", "--width", "16",
                        "--height", "16", "--number-of-plates", "2"]
            try:
                main()
            except Exception as e:
                raise e
            sys.argv = backup_argv


if __name__ == '__main__':
    unittest.main()
