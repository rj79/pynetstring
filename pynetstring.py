from enum import Enum

ZERO = ord(b'0')
NINE = ord(b'9')
COLON = ord(b':')
COMMA = ord(b',')

def _encode(data):
    if isinstance(data, str):
        data = bytes(data, 'utf-8')
    return bytes(str(len(data)), 'utf-8') + b':' + data + b','

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


class Decoder:
    def __init__(self, maxlen=0):
        self._buffer = bytearray()
        self._state = State.PARSE_LENGTH
        self._length = None
        self._decoded = []
        self._maxlen = maxlen
        self._data_offset = 0

    def feed(self, data):

        if isinstance(data, str):
            data = bytearray(data, 'utf-8')

        self._buffer = self._buffer + data

        while True:
            if self._state == State.PARSE_LENGTH:
                self._data_offset = 0
                self._length = None
                for sym in self._buffer:
                    self._data_offset += 1
                    # Avoid copy of entire buffer to cut data portion.
                    # Just track offset and use it when final string about to
                    # be extracted
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
                data_end = self._data_offset + self._length
                if len(self._buffer) < data_end + 1:
                    # The entire data part including trailing comma has not yet
                    # been received
                    break
                else:
                    if self._buffer[data_end] != COMMA:
                        raise IncompleteString('Missing trailing comma.')
                    data = self._buffer[self._data_offset:data_end]
                    self._buffer = self._buffer[data_end + 1:]
                    self._decoded.append(bytes(data))
                    self._state = State.PARSE_LENGTH

        decoded = self._decoded
        self._decoded = []
        return decoded

def decode(data):
    decoder = Decoder()
    return decoder.feed(data)
