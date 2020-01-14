import pynetstring as netstring
import unittest
import hashlib
import os

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

    def test_decode_incomplete_string_fails(self):
        with self.assertRaises(netstring.IncompleteString):
            netstring.decode('3:abc')
        with self.assertRaises(netstring.IncompleteString):
            netstring.decode('3:ab')
        with self.assertRaises(netstring.IncompleteString):
            netstring.decode('3:')
        with self.assertRaises(netstring.IncompleteString):
            netstring.decode('3')

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
        with self.assertRaises(netstring.BadLength):
            decoder.feed('-1:X,')

    def test_invalid_length_characters_raise_exception(self):
        decoder = netstring.Decoder()
        with self.assertRaises(netstring.BadLength):
            decoder.feed(b'1e2:X,')

        with self.assertRaises(netstring.BadLength):
            decoder.feed(b'+3:XXX,')

        with self.assertRaises(netstring.BadLength):
            decoder.feed(b' 3 :XXX,')

        with self.assertRaises(netstring.BadLength):
            decoder.feed(b'b\n\r\t\v\x0b\x0c +3:XXX,')
            
    def test_decoder_not_pending(self):
        decoder = netstring.Decoder()
        decoder.feed('3:abc,')
        self.assertFalse(decoder.pending())

    def test_decoder_pending(self):
        decoder = netstring.Decoder()
        decoder.feed('3:abc,0:')
        self.assertTrue(decoder.pending())

    def test_streaming_decoder_single_bytes(self):
        decoder = netstring.StreamingDecoder()
        
        self.assertEqual([], decoder.feed(b'3'))
        self.assertEqual([], decoder.feed(b':'))
        self.assertEqual([b'a'], decoder.feed(b'a'))
        self.assertEqual([b'b'], decoder.feed(b'b'))
        self.assertEqual([b'c'], decoder.feed(b'c'))
        self.assertEqual([b''], decoder.feed(b','))
        
    def test_streaming_decoder_multiple_netstrings(self):
        decoder = netstring.StreamingDecoder()

        self.assertEqual([b'ab'], decoder.feed(b'3:ab'))
        self.assertEqual([b'c', b'', b'ab', b''], decoder.feed(b'c,2:ab,'))

    def test_streaming_decoder_pending_data(self):
        decoder = netstring.StreamingDecoder()
        self.assertEqual([b'abcd',  b'', b'!!!!',  b'', b'', b'12'],
                         decoder.feed('4:abcd,4:!!!!,0:,4:12'))
        
    def xtest_100MB_netstring(self):
        block_count = 100 * 2 ** 10
        block_size = 2 ** 10
        reference_hash = hashlib.sha256()
        parsed_hash = hashlib.sha256()
        decoder = netstring.StreamingDecoder()

        # feed netstring header
        assert [] == decoder.feed(b'%d:' % (block_size * block_count))
        for _ in range(block_count):
            block = os.urandom(block_size)
            reference_hash.update(block)
            chunks = decoder.feed(block)
            assert all(chunks)
            for chunk in chunks:
                parsed_hash.update(chunk)
        # feed netstring terminator
        assert [b''] == decoder.feed(b',')
        # check encoded and decoded streams equal
        assert reference_hash.digest() == parsed_hash.digest()
