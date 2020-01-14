from enum import Enum

ZERO = ord(b'0')
NINE = ord(b'9')
COLON = ord(b':')
COMMA = ord(b',')
EMPTY = b''

def _encode(data):
    if isinstance(data, str):
        data = bytes(data, 'utf-8')
    return b'%d:%s,' % (len(data), data)

def encode(data):
    if isinstance(data, list):
        return [_encode(x) for x in data]
    return _encode(data)


class NetstringException(Exception):
    pass


class ParseError(NetstringException):
    pass


class TooLong(ParseError):
    pass


class BadLength(ParseError):
    pass


class IncompleteString(ParseError):
    pass


class State(Enum):
    PARSE_LENGTH = 0
    PARSE_DATA = 1
    PARSE_TERMINATOR = 2


class StreamingDecoder:
    def __init__(self, maxlen=0):
        self._state = State.PARSE_LENGTH
        self._length = None
        self._maxlen = maxlen

    def pending(self):
        return not (self._state == State.PARSE_LENGTH and self._length is None)

    def feed(self, data):

        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        len_data = len(data)

        decoded = []
        input_offset = 0

        while input_offset < len_data:
            if self._state == State.PARSE_LENGTH:
                for sym in data[input_offset:]:
                    input_offset += 1
                    if ZERO <= sym <= NINE:
                        if self._length is None:
                            self._length = sym - ZERO
                        else:
                            self._length = self._length * 10 + sym - ZERO
                        if self._maxlen and self._length > self._maxlen:
                            raise TooLong('Specified netstring length '
                                          'is over decoder limit.')
                    elif sym == COLON:
                        if self._length is None:
                            raise BadLength('No netstring length bytes read.')
                        self._state = State.PARSE_DATA
                        break
                    else:
                        raise BadLength('Invalid symbol found in netstring '
                                        'length: %s' % repr(bytes((sym,))))
                else:
                    # Entire buffer was scanned, but no complete length was read
                    break
            if self._state == State.PARSE_DATA:
                if self._length == 0:
                    self._state = State.PARSE_TERMINATOR
                else:
                    bytes_remaining = len_data - input_offset
                    if bytes_remaining == 0:
                        break
                    yield_size = min(self._length, bytes_remaining)
                    yield_buf = data[input_offset:input_offset + yield_size]
                    self._length -= yield_size
                    input_offset += yield_size
                    decoded.append(yield_buf)
            if self._state == State.PARSE_TERMINATOR:
                if input_offset >= len_data:
                    break
                if data[input_offset] != COMMA:
                    raise IncompleteString('Missing trailing comma.')
                input_offset += 1
                decoded.append(EMPTY)
                self._state = State.PARSE_LENGTH
                self._length = None

        return decoded


class Decoder:
    def __init__(self, maxlen=0):
        self._decoder = StreamingDecoder(maxlen)
        self._pending = []

    def pending(self):
        return self._decoder.pending()

    def feed(self, data):
        res = []

        parts = self._decoder.feed(data)
        for part in parts:
            if part:
                self._pending.append(part)
            else:
                res.append(EMPTY.join(self._pending))
                self._pending.clear()

        return res


def decode(data):
    decoder = Decoder()
    res = decoder.feed(data)
    if decoder.pending():
        raise IncompleteString("Input ends on unfinished string.")
    return res
