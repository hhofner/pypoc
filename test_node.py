import unittest
import simple_node
import generation_models

class TestSimpleNodeMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.test_node = simple_node.Node()

    def testUpdateMethod(self) -> None:
        test_kwargs = [ {'generation_rate': 100,
                       'destinations': [1,2,3,4,5],
                       'type': 'node',
                       'serv_rate': 100,
                       'queue_cap': 100,
                       'gen_scheme': 'linear',
                       'logging_file': 'tpp',}, ]

        for tk in test_kwargs:
            self.test_node.update(**tk)
            for key in tk.keys():
                self.assertEqual(tk[key], self.test_node.config[key])

    def testGeneratePacketsMethodSet(self):
        pass

    def testTransmitMethod(self):
        pass

if __name__ == '__main__':
    unittest.main()