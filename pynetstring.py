from enum import Enum

def _encode(data):
    if isinstance(data, str):
        data = bytes(data, 'utf-8')
    return bytes(str(len(data)), 'utf-8') + b':' + data + b','

def encode(data):
    if isinstance(data, list):
        return [_encode(x) for x in data]
    return _encode(data)


class State(Enum):
    PARSE_LENGTH = 0
    PARSE_DATA = 1


class Decoder:
    def __init__(self):
        self._buffer = bytearray()
        self._state = State.PARSE_LENGTH
        self._length = None
        self._decoded = []

    def feed(self, data):

        if isinstance(data, str):
            data = bytearray(data, 'utf-8')

        self._buffer = self._buffer + data

        while True:
            if self._state == State.PARSE_LENGTH:
                length_end = self._buffer.find(b':')
                if length_end == -1:
                    # There is not enough data yet to decode the length
                    break
                else:
                    self._length = int(self._buffer[:length_end])
                    if self._length > 0 and self._buffer[0] == ord(b'0'):
                        raise ValueError('Leading zero in non-empty netstring.')
                    # Consume what has been parsed
                    self._buffer = self._buffer[length_end + 1:]
                    self._state = State.PARSE_DATA

            if self._state == State.PARSE_DATA:
                if len(self._buffer) < self._length + 1:
                    # The entire data part including trailing comma has not yet
                    # been received
                    break
                else:
                    if self._buffer[self._length] != ord(b','):
                        raise ValueError('Missing trailing comma.')
                    data = self._buffer[:self._length]
                    self._buffer = self._buffer[self._length + 1:]
                    self._decoded.append(bytes(data))
                    self._state = State.PARSE_LENGTH

        decoded = self._decoded
        self._decoded = []
        return decoded

def decode(data):
    decoder = Decoder()
    return decoder.feed(data)
