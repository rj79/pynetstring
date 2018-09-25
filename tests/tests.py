import pynetstring as netstring
import unittest

class TestNetString(unittest.TestCase):

    def test_encode_empty_string(self):
        self.assertEqual(b'0:,', netstring.encode(''))
        self.assertEqual(b'0:,', netstring.encode(b''))

    def test_leading_zero_in_length_raises_exception_if_data_nonempty(self):
        with self.assertRaises(Exception):
            self.decode('01:X,')

    def test_decode_empty_string(self):
        self.assertEqual([b''], netstring.decode(b'0:,'))

    def test_decode_missing_comma_fails(self):
        with self.assertRaises(Exception):
            self.decode('3:abc_')

    def test_encode_one_byte_string(self):
        self.assertEqual(b'1:X,', netstring.encode('X'))
        self.assertEqual(b'1:X,', netstring.encode(b'X'))

    def test_decode_nested(self):
        self.assertEqual([b'5:Hello,6:World!'], netstring.decode('16:5:Hello,6:World!,,'))

    def test_feed_empty_string_partially(self):
        decoder = netstring.Decoder()
        self.assertEqual([], decoder.feed('0'))
        self.assertEqual([], decoder.feed(':'))
        self.assertEqual([b''], decoder.feed(','))

    def test_feed_multiple(self):
        sequence = '4:this,2:is,1:a,4:test,'
        self.assertEqual([b'this', b'is', b'a', b'test'], netstring.decode(sequence))

    def test_feed_multiple_and_partial(self):
        decoder = netstring.Decoder()
        self.assertEqual([], decoder.feed('1:'))
        self.assertEqual([b'X', b'abc'], decoder.feed('X,3:abc,2:'))
        self.assertEqual([b'ok'], decoder.feed('ok,'))

    def test_encode_sequence(self):
        self.assertEqual([b'3:foo,', b'3:bar,'], netstring.encode(['foo', 'bar']))
