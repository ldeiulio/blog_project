import os
import unittest
import datetime
from app import has_next, has_prev


if "CONFIG_PATH" not in os.environ:
    os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"


class MyTestCase(unittest.TestCase):

    # determines if has_next is outputting correctly based on expected inputs
    def test_has_next(self):
        self.assertTrue(has_next(1,2))
        self.assertFalse(has_next(2,2))
        self.assertFalse((has_next(2,1)))

    # determines if has_prev is outputting correctly based on expected inputs
    def test_has_prev(self):
        self.assertTrue(has_prev(2))
        self.assertFalse(has_prev(1))
        self.assertFalse(has_prev(0))


if __name__ == '__main__':
    unittest.main()
