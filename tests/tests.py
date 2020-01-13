import pynetstring as netstring
import unittest

class TestNetString(unittest.TestCase):

    def test_encode_empty_string(self):
        self.assertEqual(b'0:,', netstring.encode(''))
        self.assertEqual(b'0:,', netstring.encode(b''))

    def test_accept_leading_zero(self):
        self.assertEqual([b'X'], netstring.decode('01:X,'))

    def test_decode_empty_string(self):
        self.assertEqual([b''], netstring.decode(b'0:,'))

    def test_decode_missing_comma_fails(self):
        with self.assertRaises(netstring.IncompleteString):
            netstring.decode('3:abc_')

    def test_encode_one_byte_string(self):
        self.assertEqual(b'1:X,', netstring.encode('X'))
        self.assertEqual(b'1:X,', netstring.encode(b'X'))

    def test_decode_nested(self):
        self.assertEqual([b'5:Hello,6:World!,'], netstring.decode('17:5:Hello,6:World!,,'))

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

    def test_no_limit_error_when_content_shorter(self):
        decoder = netstring.Decoder(10)
        try:
            self.assertEqual([b'XXXXXXXXX'], decoder.feed(b'9:XXXXXXXXX,'))
        except netstring.TooLong:
            self.assertFalse(True)

    def test_no_limit_error_when_content_just_right(self):
        decoder = netstring.Decoder(1)
        try:
            self.assertEqual([b'X'], decoder.feed(b'1:X,'))
        except netstring.TooLong:
            self.assertFalse(True)

        decoder = netstring.Decoder(10)
        try:
            self.assertEqual([b'XXXXXXXXXX'], decoder.feed(b'10:XXXXXXXXXX,'))
        except netstring.TooLong:
            self.assertFalse(True)

    def test_limit_error_when_content_too_long(self):
        decoder = netstring.Decoder(1)
        with self.assertRaises(netstring.TooLong):
            decoder.feed(b'2:XX,')

    def test_limit_error_when_missing_comma(self):
        decoder = netstring.Decoder(10)
        with self.assertRaises(netstring.IncompleteString):
            decoder.feed(b'10:XXXXXXXXXXX,')

    def test_limit_error_when_length_declaration_inplausibly_long(self):
        decoder = netstring.Decoder(100)
        with self.assertRaises(netstring.TooLong):
            # The length declaration of a netstring with content of 100 bytes
            # takes up at most log10(100) + 1 = 3 bytes.
            # Error raised already here because 4 bytes of length parsed but
            # no length end marker ":" found yet.
            decoder.feed(b'1000')
            
    def test_handle_negative_length(self):
        decoder = netstring.Decoder()
        with self.assertRaises(netstring.ParseError):
            decoder.feed('-1:X,')
