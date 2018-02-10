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

  netstring_bytes = pynetstring.encode('Hello')
  # Will give b'Hello'
  print(netstring_bytes)

**Decoding**

In the simplest case, when we know for sure that the data we are trying to
decode ends on a netstring boundary we can simply do:
::

  # data_list will be an list of bytes.
  decoded_list = pynetstring.decode('5:Hello,6:World!')
  # Will give [b'Hello', b'World!']
  print(decoded_list)

In many cases however, such when netstring data is transmitted over a network,
the chunks of data that arrive may not align to netstring boundaries.
For example a chunk of data may contain a netstring and then parts of the next.
To handle this, call Decoder.feed(), which will parse the data and emit decoded
data as soon as it has been fully received.
::

  decoder = pynetstring.Decoder()
  # Will give []
  print(decoder.feed('5:He'))
  # Will give [b'Hello', b'World!']
  print(decoder.feed('llo,6:World!,5:ag'))
  # Will give [b'again']
  print(decoder.feed('ain,'))


The receiving side could look something like this:
::

  decoder = pynetstring.Decoder()

  def handle_network_data(data):
    decoded_list = decoder.feed(data)
    for item in decoded_list:
        print(item)

Data encoding
-------------
Regardless of the type of the data that is sent to encode(), it will always
return binary data, i.e. python bytes. The data that is returned from decode()
and Decoder.feed() will also be binary. This is because the decoder can not
make any assumptions on the encoding of the original data. If you know that the
data that comes in can be interpreted in a particular way or encoding, e.g.
UTF-8, you have to explicitly do that conversion.
::

  encoded = pynetstring.encode(u'Hello World!')
  # This will be <class 'bytes'>
  print(type(encoded))
  decoded_list = pynetstring.decode(encoded)
  # This will be <class 'bytes'>
  print(type(decoded_list[0]))
  # This will return the original unicode string u'Hello World!'
  print(decoded_list[0].decode('utf-8'))
