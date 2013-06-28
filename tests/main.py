import unittest


def main():
    print "Running tests"
    suite = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
