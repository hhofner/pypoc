import simpy
import unittest
import node
import exceptions

class TestBaseNodeMethods(unittest.TestCase):
    def setUp(self):
        self.kwargs = {'x':1,
                  'y':1,
                  'z':1, }
        self.node = node.Node(**self.kwargs)
        self.env = simpy.Environment()

    def test_init(self):
        """ Test if the initializer worked properly
            without the env initialization
        """
        self.assertEqual(self.node.x, 1)
        self.assertEqual(self.node.y, 1)
        self.assertEqual(self.node.z, 1)

    # @unittest.expectedFailure
    # def test_env_absence(self):
    #     """ Test if the absence of env variable in node
    #         is true
    #     """
    #     self.assertEqual(self.node.env, self.env)

    def test_env_absence(self):
        with self.assertRaises(AttributeError):
            print(self.node.env)

    def test_init_with_env(self):
        """ Test if exception is raised when env
            is added as argument in initializer
        """
        self.kwargs['env'] = self.env
        with self.assertRaises(exceptions.RunMethodEmpty):
            node.Node(**self.kwargs)

if __name__ == "__main__":
    unittest.main()
