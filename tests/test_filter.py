import os
import unittest
import datetime


if "CONFIG_PATH" not in os.environ:
    os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"



class MyTestCase(unittest.TestCase):
    def test_something(self):
        print("test")
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
