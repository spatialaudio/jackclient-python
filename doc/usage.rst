Usage
=====

First, import the module:

>>> import jack

Then, you most likely want to create a new `jack.Client`:

>>> client = jack.Client('MyGreatClient')

You probably want to create some audio input and output ports, too:

>>> client.inports.register('input_1')
jack.OwnPort('MyGreatClient:input_1')
>>> client.outports.register('output_1')
jack.OwnPort('MyGreatClient:output_1')

As you can see, these functions return the newly created port.
If you want, you can save it for later:

>>> in2 = client.inports.register('input_2')
>>> out2 = client.outports.register('output_2')

To see what you can do with the returned objects, have a look at the
documentation of the class `jack.OwnPort`.

In case you forgot, you should remind yourself about the ports you just created:

>>> client.inports
[jack.OwnPort('MyGreatClient:input_1'), jack.OwnPort('MyGreatClient:input_2')]
>>> client.outports
[jack.OwnPort('MyGreatClient:output_1'), jack.OwnPort('MyGreatClient:output_2')]

Have a look at the documentation of the class `jack.Ports` to get more detailed
information about these lists of ports.

If you have selected an appropriate driver in your JACK settings, you can also
create MIDI ports:

>>> client.midi_inports.register('midi_in')
jack.OwnMidiPort('MyGreatClient:midi_in')
>>> client.midi_outports.register('midi_out')
jack.OwnMidiPort('MyGreatClient:midi_out')

You can check what other JACK ports are available (your output may be
different):

>>> client.get_ports()  # doctest: +SKIP
[jack.Port('system:capture_1'),
 jack.Port('system:capture_2'),
 jack.Port('system:playback_1'),
 jack.Port('system:playback_2'),
 jack.MidiPort('system:midi_capture_1'),
 jack.MidiPort('system:midi_playback_1'),
 jack.OwnPort('MyGreatClient:input_1'),
 jack.OwnPort('MyGreatClient:output_1'),
 jack.OwnPort('MyGreatClient:input_2'),
 jack.OwnPort('MyGreatClient:output_2'),
 jack.OwnMidiPort('MyGreatClient:midi_in'),
 jack.OwnMidiPort('MyGreatClient:midi_out')]

Note that the ports you created yourself are of type `jack.OwnPort` and
`jack.OwnMidiPort`, while other ports are merely of type `jack.Port` and
`jack.MidiPort`, respectively.

You can also be more specific when looking for ports:

>>> client.get_ports(is_audio=True, is_output=True, is_physical=True)
[jack.Port('system:capture_1'), jack.Port('system:capture_2')]

You can even use regular expressions to search for ports:

>>> client.get_ports('Great.*2$')
[jack.OwnPort('MyGreatClient:input_2'), jack.OwnPort('MyGreatClient:output_2')]

If you want, you can also set all kinds of callback functions for your client.
For details see the documentation for the class `jack.Client` and the example
applications in the ``examples/`` directory.

Once you are ready to run, you should activate your client:

>>> client.activate()

As soon as the client is activated, you can make connections (this isn't
possible before activating the client):

>>> client.connect('system:capture_1', 'MyGreatClient:input_1')
>>> client.connect('MyGreatClient:output_1', 'system:playback_1')

You can also use the port objects from before instead of port names:

>>> client.connect(out2, 'system:playback_2')
>>> in2.connect('system:capture_2')

Use `jack.Client.get_all_connections()` to find out which other ports are
connected to a given port.
If you own the port, you can also use `jack.OwnPort.connections`.

>>> client.get_all_connections('system:playback_1')
[jack.OwnPort('MyGreatClient:output_1')]
>>> out2.connections
[jack.Port('system:playback_2')]

Of course you can also disconnect ports, there are again several possibilities:

>>> client.disconnect('system:capture_1', 'MyGreatClient:input_1')
>>> client.disconnect(out2, 'system:playback_2')
>>> in2.disconnect()  # disconnect all connections with in2

If you don't need your ports anymore, you can un-register them:

>>> in2.unregister()
>>> client.outports.clear()  # unregister all audio output ports

Finally, you can de-activate your JACK client and close it:

>>> client.deactivate()
>>> client.close()
