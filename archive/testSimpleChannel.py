'''
Testing script for SimpleChannel classes.
'''
import unittest
from collections import namedtuple, deque
from simple_channel import SimpleChannel

__author__ = 'Hans Hofner'


class TestSimpleChannelMethods(unittest.TestCase):
    def setUp(self):
        self.chan = SimpleChannel(name='test',
                                  bandwidth=10,
                                  step_m=1)

    def testLimitlessReceivePackets(self):
        Packet = namedtuple('Packet', 'size, src, dest, path')
        p = Packet(1, 1, 2, '1-2-3')
        self.chan.receive([p])
        self.assertEqual(self.chan._packets_in_channel,
                         deque([p]), 'packets is different')

    def testChannelLoadMechanism(self):
        Packet = namedtuple('Packet', 'size, src, dest, path')
        p = [Packet(1, 1, 2, '1-2-3'), Packet(2, 1, 2, '1-2-3')]
        self.chan.receive(p)
        self.assertEqual(self.chan.current_channel_load, 3)

    def testEmptyToTransmit(self):
        Packet = namedtuple('Packet', 'size, src, dest, path')
        p = [Packet(1, 1, 2, '1-2-3'), Packet(2, 1, 2, '1-2-3')]
        self.chan.receive(p)
        self.assertEqual(self.chan._to_transmit,
                         [])

    def testEmptyPacketsChannelAfterUpdate(self):
        Packet = namedtuple('Packet', 'size, src, dest, path')
        p = [Packet(1, 1, 2, '1-2-3'), Packet(2, 1, 2, '1-2-3')]
        self.chan.receive(p)
        self.chan.update()
        self.assertEqual(self.chan._packets_in_channel,
                         deque([]))

    def testNewToTransmitAfterUpdate(self):
        Packet = namedtuple('Packet', 'size, src, dest, path')
        p = [Packet(1, 1, 2, '1-2-3'), Packet(2, 1, 2, '1-2-3')]
        self.chan.receive(p)
        self.chan.update()
        self.assertEqual(self.chan._to_transmit,
                         p)

    def testGetPacketsAfterUpdate(self):
        Packet = namedtuple('Packet', 'size, src, dest, path')
        DummyNode = namedtuple('Node', 'id')
        p = [Packet(1, 1, 2, '1-2-3'), Packet(2, 1, 2, '1-2-3')]
        n1 = DummyNode(1)
        n2 = DummyNode(2)
        self.chan.receive(p)
        self.chan.update()
        r = self.chan.get_packets(n1, n2)
        self.assertEqual(r, p)


if __name__ == '__main__':
    unittest.main()
