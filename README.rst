===========
pynetstring
===========
A module for encoding and decoding netstrings. See the definition of netstrings
at https://cr.yp.to/proto/netstrings.txt.

Requirements
------------
Pynetstring is written for Python 3.

Usage
-----
**Encoding**
::

  # Will give b'5:Hello,'
  print(pynetstring.encode('Hello'))

It is also possible to encode lists of data.
::

  # Will give [b'5:Hello,', b'5:World,']
  print(pynetstring.encode(['Hello', 'World']))

**Decoding**

In the simplest case, when we know for sure that the data we are trying to
decode ends on a netstring boundary we can simply do:
::
  
  # Will give [b'Hello', b'World!']
  print(pynetstring.decode('5:Hello,6:World!,'))
  
In many cases however, such when netstring are transmitted over a network, the
chunks of data that arrive may not necessarily align to netstring boundaries.
For example a chunk of data may contain a netstring and then parts of the next.
To handle this, call Decoder.feed(), which will buffer and parse the data and 
emit decoded data as soon as one or more netstrings have been fully received.
::

  decoder = pynetstring.Decoder()
  # Will give []
  print(decoder.feed('5:He'))
  # Will give ['Hello', 'World!']
  print(decoder.feed('llo,6:World!,5:ag'))
  # Will give ['again']
  print(decoder.feed('ain,'))


The receiving side could look something like this:
::

  decoder = pynetstring.Decoder()

  def handle_network_data(data):
    decoded_list = decoder.feed(data)
    for item in decoded_list:
        print(item)

Also the Decoder class supports limiting the maximal decoded netstring length.
This is required for network applications to restrict the maximal length of 
the input buffer in order to prevent unintentional memory bloat or intentional 
misuse from malicious senders.
The netstring length limit is optional and specified as the first argument to 
the constructor:
::

  decoder = pynetstring.Decoder(maxlen=1024)

The Decoder will raise TooLong exception as soon as it'll discover next string
can't fit the limit.

Data encoding
-------------
Regardless of the type of the data that is sent to encode(), it will always
return binary data, i.e. python bytes. The data that is returned from decode()
and Decoder.feed() will also be binary. This is because the decoder can not
make any assumptions on the encoding of the original data. If you know that 
the data that comes in can be interpreted in a particular way or encoding, 
e.g. UTF-8, you have to explicitly do that conversion.
::

  encoded = pynetstring.encode(u'Hello World!')
  # This will be <class 'bytes'>
  print(type(encoded))
  decoded_list = pynetstring.decode(encoded)
  # This will be <class 'bytes'>
  print(type(decoded_list[0]))
  # This will return the original unicode string u'Hello World!'
  print(decoded_list[0].decode('utf-8'))

Error handling
--------------
A ParseError subclass exception will be raised if trying to decode an invalid 
netstring.
::

  # IncompleteString exception due to missing trailing comma:
  pynetstring.decode('3:ABC_')

  decoder = Decoder(3)
  # TooLong exception due to exceeded netstring limit in stream parser:
  decoder.feed(b'4:ABCD,')

  # ParseError due to negative length
  decoder.feed(b'-1:X,')

All other exceptions of this module can be expected to be subclass of 
NetstringException.
