# Copyright (c) 2014-2020 Matthias Geier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""JACK Client for Python.

http://jackclient-python.readthedocs.io/

"""
__version__ = '0.5.3'

from ctypes.util import find_library as _find_library
import errno as _errno
import platform as _platform
import warnings as _warnings

from _jack import ffi as _ffi

if _platform.system() == 'Windows':
    if _platform.architecture()[0] == '64bit':
        _libname = _find_library('libjack64')
    else:
        _libname = _find_library('libjack')
else:
    _libname = _find_library('jack')

if _libname is None:
    raise OSError('JACK library not found')
_lib = _ffi.dlopen(_libname)

_AUDIO = b'32 bit float mono audio'
_MIDI = b'8 bit raw midi'

STOPPED = _lib.JackTransportStopped
"""Transport halted."""
ROLLING = _lib.JackTransportRolling
"""Transport playing."""
STARTING = _lib.JackTransportStarting
"""Waiting for sync ready."""
NETSTARTING = _lib.JackTransportNetStarting
"""Waiting for sync ready on the network."""

PROPERTY_CREATED = _lib.PropertyCreated
"""A property was created.  See `Client.set_property_change_callback()`."""
PROPERTY_CHANGED = _lib.PropertyChanged
"""A property was changed.  See `Client.set_property_change_callback()`."""
PROPERTY_DELETED = _lib.PropertyDeleted
"""A property was deleted.  See `Client.set_property_change_callback()`."""

POSITION_BBT = _lib.JackPositionBBT
"""Bar, Beat, Tick."""
POSITION_TIMECODE = _lib.JackPositionTimecode
"""External timecode."""
POSITION_BBT_FRAME_OFFSET = _lib.JackBBTFrameOffset
"""Frame offset of BBT information."""
POSITION_AUDIO_VIDEO_RATIO = _lib.JackAudioVideoRatio
"""Audio frames per video frame."""
POSITION_VIDEO_FRAME_OFFSET = _lib.JackVideoFrameOffset
"""Frame offset of first video frame."""

_SUCCESS = 0
_FAILURE = 1


def _decode(cdata):
    return _ffi.string(cdata).decode()


# Get metadata constants from library
for name in dir(_lib):
    if name.startswith('JACK_METADATA_'):
        try:
            globals()[name[5:]] = _decode(getattr(_lib, name))
        except _ffi.error:
            pass
else:
    del name


class JackError(Exception):
    """Exception for all kinds of JACK-related errors."""


class JackErrorCode(JackError):

    def __init__(self, message, code):
        """Exception for JACK errors with an error code.

        Subclass of `JackError`.

        The following attributes are available:

        Attributes
        ----------
        message
            Error message.
        code
            The error code returned by the JACK library function which
            resulted in this exception being raised.

        """
        self.message = message
        self.code = code

    def __str__(self):
        return '{} ({})'.format(self.message, self.code)


class JackOpenError(JackError):

    def __init__(self, name, status):
        """Exception raised for errors while creating a JACK client.

        Subclass of `JackError`.

        The following attributes are available:

        Attributes
        ----------
        name
            Requested client name.
        status
            A :class:`Status` instance representing the status information
            received by the ``jack_client_open()`` JACK library call.

        """
        self.name = name
        self.status = status

    def __str__(self):
        return 'Error initializing "{}": {}'.format(self.name, self.status)


class Client(object):
    """A client that can connect to the JACK audio server."""

    def __init__(self, name, use_exact_name=False, no_start_server=False,
                 servername=None, session_id=None):
        """Create a new JACK client.

        A client object is a *context manager*, i.e. it can be used in a
        *with statement* to automatically call `activate()` in the
        beginning of the statement and `deactivate()` and `close()` on
        exit.

        Parameters
        ----------
        name : str
            The desired client name of at most `client_name_size()`
            characters.  The name scope is local to each server.
            Unless forbidden by the *use_exact_name* option, the server
            will modify this name to create a unique variant, if needed.

        Other Parameters
        ----------------
        use_exact_name : bool
            Whether an error should be raised if *name* is not unique.
            See `Status.name_not_unique`.
        no_start_server : bool
            Do not automatically start the JACK server when it is not
            already running.  This option is always selected if
            ``JACK_NO_START_SERVER`` is defined in the calling process
            environment.
        servername : str
            Selects from among several possible concurrent server
            instances.
            Server names are unique to each user.  If unspecified, use
            ``'default'`` unless ``JACK_DEFAULT_SERVER`` is defined in
            the process environment.
        session_id : str
            Pass a SessionID Token. This allows the sessionmanager to
            identify the client again.

        Raises
        ------
        JackOpenError
            If the session with the JACK server could not be opened.

        """
        status = _ffi.new('jack_status_t*')
        options = _lib.JackNullOption
        optargs = []
        if use_exact_name:
            options |= _lib.JackUseExactName
        if no_start_server:
            options |= _lib.JackNoStartServer
        if servername:
            options |= _lib.JackServerName
            optargs.append(_ffi.new('char[]', servername.encode()))
        if session_id:
            options |= _lib.JackSessionID
            optargs.append(_ffi.new('char[]', session_id.encode()))
        self._ptr = _lib.jack_client_open(name.encode(), options, status,
                                          *optargs)
        self._status = Status(status[0])
        if not self._ptr:
            raise JackOpenError(name, self._status)

        self._inports = Ports(self, _AUDIO, _lib.JackPortIsInput)
        self._outports = Ports(self, _AUDIO, _lib.JackPortIsOutput)
        self._midi_inports = Ports(self, _MIDI, _lib.JackPortIsInput)
        self._midi_outports = Ports(self, _MIDI, _lib.JackPortIsOutput)
        self._keepalive = []
        self._position = _ffi.new('jack_position_t*')

    # Avoid confusion if something goes wrong before opening the client:
    _ptr = _ffi.NULL

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, *args):
        self.deactivate()
        self.close()

    def __del__(self):
        """Close JACK client on garbage collection."""
        self.close()

    @property
    def name(self):
        """The name of the JACK client (read-only)."""
        return _decode(_lib.jack_get_client_name(self._ptr))

    @property
    def uuid(self):
        """The UUID of the JACK client (read-only).

        Raises
        ------
        JackError
            If getting the UUID fails.

        """
        uuid = _ffi.gc(_lib.jack_client_get_uuid(self._ptr), _lib.jack_free)
        if not uuid:
            raise JackError('Unable to get UUID')
        return _decode(uuid)

    @property
    def samplerate(self):
        """The sample rate of the JACK system (read-only)."""
        return _lib.jack_get_sample_rate(self._ptr)

    @property
    def blocksize(self):
        """The JACK block size (must be a power of two).

        The current maximum size that will ever be passed to the process
        callback.  It should only be queried *before* `activate()` has
        been called.  This size may change, clients that depend on it
        must register a callback with `set_blocksize_callback()` so they
        will be notified if it does.

        Changing the blocksize stops the JACK engine process cycle, then
        calls all registered callback functions (see
        `set_blocksize_callback()`) before restarting the process
        cycle.  This will cause a gap in the audio flow, so it should
        only be done at appropriate stopping points.

        """
        return _lib.jack_get_buffer_size(self._ptr)

    @blocksize.setter
    def blocksize(self, blocksize):
        _check(_lib.jack_set_buffer_size(self._ptr, blocksize),
               'Error setting JACK blocksize')

    @property
    def status(self):
        """JACK client status.  See `Status`."""
        return self._status

    @property
    def realtime(self):
        """Whether JACK is running with ``-R`` (``--realtime``)."""
        return bool(_lib.jack_is_realtime(self._ptr))

    @property
    def frames_since_cycle_start(self):
        """Time since start of audio block.

        The estimated time in frames that has passed since the JACK
        server began the current process cycle.

        """
        return _lib.jack_frames_since_cycle_start(self._ptr)

    @property
    def frame_time(self):
        """The estimated current time in frames.

        This is intended for use in other threads (not the process
        callback).  The return value can be compared with the value of
        `last_frame_time` to relate time in other threads to JACK time.

        """
        return _lib.jack_frame_time(self._ptr)

    @property
    def last_frame_time(self):
        """The precise time at the start of the current process cycle.

        This may only be used from the process callback (see
        `set_process_callback()`), and can be used to interpret
        timestamps generated by `frame_time` in other threads with
        respect to the current process cycle.

        This is the only jack time function that returns exact time:
        when used during the process callback it always returns the same
        value (until the next process callback, where it will return
        that value + `blocksize`, etc).  The return value is guaranteed
        to be monotonic and linear in this fashion unless an xrun occurs
        (see `set_xrun_callback()`).  If an xrun occurs, clients must
        check this value again, as time may have advanced in a
        non-linear way (e.g.  cycles may have been skipped).

        """
        return _lib.jack_last_frame_time(self._ptr)

    @property
    def inports(self):
        """A list of audio input `Ports`.

        New ports can be created and added to this list with
        `inports.register() <Ports.register>`.
        When :meth:`~OwnPort.unregister` is called on one of the items
        in this list, this port is removed from the list.
        `inports.clear() <Ports.clear>` can be used to unregister all
        audio input ports at once.

        See Also
        --------
        Ports, OwnPort

        """
        return self._inports

    @property
    def outports(self):
        """A list of audio output :class:`Ports`.

        New ports can be created and added to this list with
        `outports.register() <Ports.register>`.
        When :meth:`~OwnPort.unregister` is called on one of the items
        in this list, this port is removed from the list.
        `outports.clear() <Ports.clear>` can be used to unregister all
        audio output ports at once.

        See Also
        --------
        Ports, OwnPort

        """
        return self._outports

    @property
    def midi_inports(self):
        """A list of MIDI input :class:`Ports`.

        New MIDI ports can be created and added to this list with
        `midi_inports.register() <Ports.register>`.
        When :meth:`~OwnPort.unregister` is called on one of the items
        in this list, this port is removed from the list.
        `midi_inports.clear() <Ports.clear>` can be used to unregister
        all MIDI input ports at once.

        See Also
        --------
        Ports, OwnMidiPort

        """
        return self._midi_inports

    @property
    def midi_outports(self):
        """A list of MIDI output :class:`Ports`.

        New MIDI ports can be created and added to this list with
        `midi_outports.register() <Ports.register>`.
        When :meth:`~OwnPort.unregister` is called on one of the items
        in this list, this port is removed from the list.
        `midi_outports.clear() <Ports.clear>` can be used to unregister
        all MIDI output ports at once.

        See Also
        --------
        Ports, OwnMidiPort

        """
        return self._midi_outports

    def owns(self, port):
        """Check if a given port belongs to *self*.

        Parameters
        ----------
        port : str or Port
            Full port name or `Port`, `MidiPort`, `OwnPort` or
            `OwnMidiPort` object.

        """
        port = self._get_port_ptr(port)
        return bool(_lib.jack_port_is_mine(self._ptr, port))

    def activate(self):
        """Activate JACK client.

        Tell the JACK server that the program is ready to start
        processing audio.

        """
        _check(_lib.jack_activate(self._ptr), 'Error activating JACK client')

    def deactivate(self, ignore_errors=True):
        """De-activate JACK client.

        Tell the JACK server to remove *self* from the process graph.
        Also, disconnect all ports belonging to it, since inactive
        clients have no port connections.

        """
        err = _lib.jack_deactivate(self._ptr)
        if not ignore_errors:
            _check(err, 'Error deactivating JACK client')

    def cpu_load(self):
        """Return the current CPU load estimated by JACK.

        This is a running average of the time it takes to execute a full
        process cycle for all clients as a percentage of the real time
        available per cycle determined by `blocksize` and `samplerate`.

        """
        return _lib.jack_cpu_load(self._ptr)

    def close(self, ignore_errors=True):
        """Close the JACK client."""
        if self._ptr:
            err = _lib.jack_client_close(self._ptr)
            self._ptr = _ffi.NULL
            if not ignore_errors:
                _check(err, 'Error closing JACK client')

    def connect(self, source, destination):
        """Establish a connection between two ports.

        When a connection exists, data written to the source port will
        be available to be read at the destination port.

        Audio ports can obviously not be connected with MIDI ports.

        Parameters
        ----------
        source : str or Port
            One end of the connection. Must be an output port.
        destination : str or Port
            The other end of the connection. Must be an input port.

        See Also
        --------
        OwnPort.connect, disconnect

        Raises
        ------
        JackError
            If there is already an existing connection between *source* and
            *destination* or the connection can not be established.

        """
        if isinstance(source, Port):
            source = source.name
        if isinstance(destination, Port):
            destination = destination.name
        err = _lib.jack_connect(self._ptr, source.encode(),
                                destination.encode())
        if err == _errno.EEXIST:
            raise JackErrorCode('Connection {0!r} -> {1!r} '
                                'already exists'.format(source, destination),
                                err)
        _check(err,
               'Error connecting {0!r} -> {1!r}'.format(source, destination))

    def disconnect(self, source, destination):
        """Remove a connection between two ports.

        Parameters
        ----------
        source, destination : str or Port
            See `connect()`.

        """
        if isinstance(source, Port):
            source = source.name
        if isinstance(destination, Port):
            destination = destination.name
        _check(_lib.jack_disconnect(
            self._ptr, source.encode(), destination.encode()),
            "Couldn't disconnect {0!r} -> {1!r}".format(source, destination))

    def transport_start(self):
        """Start JACK transport."""
        _lib.jack_transport_start(self._ptr)

    def transport_stop(self):
        """Stop JACK transport."""
        _lib.jack_transport_stop(self._ptr)

    @property
    def transport_state(self):
        """JACK transport state.

        This is one of `STOPPED`, `ROLLING`, `STARTING`, `NETSTARTING`.

        See Also
        --------
        transport_query

        """
        return TransportState(_lib.jack_transport_query(self._ptr, _ffi.NULL))

    @property
    def transport_frame(self):
        """Get/set current JACK transport frame.

        Return an estimate of the current transport frame, including any
        time elapsed since the last transport positional update.
        Assigning a frame number repositions the JACK transport.

        """
        return _lib.jack_get_current_transport_frame(self._ptr)

    @transport_frame.setter
    def transport_frame(self, frame):
        _check(_lib.jack_transport_locate(self._ptr, frame),
               'Error locating JACK transport')

    def transport_locate(self, frame):
        """

        .. deprecated:: 0.4.1
            Use `transport_frame` instead

        """
        _warnings.warn(
            'transport_locate() is deprecated, use transport_frame',
            DeprecationWarning)
        self.transport_frame = frame

    def transport_query(self):
        """Query the current transport state and position.

        This is a convenience function that does the same as
        `transport_query_struct()`, but it only returns the valid fields
        in an easy-to-use ``dict``.

        Returns
        -------
        state : TransportState
            The transport state can take following values:
            `STOPPED`, `ROLLING`, `STARTING` and `NETSTARTING`.
        position : dict
            A dictionary containing only the valid fields of the
            structure returned by `transport_query_struct()`.

        See Also
        --------
        :attr:`transport_state`, transport_query_struct

        """
        state, pos = self.transport_query_struct()
        return TransportState(state), position2dict(pos)

    def transport_query_struct(self):
        """Query the current transport state and position.

        This function is realtime-safe, and can be called from any
        thread.  If called from the process thread, the returned
        position corresponds to the first frame of the current cycle and
        the state returned is valid for the entire cycle.

        Returns
        -------
        state : int
            The transport state can take following values: `STOPPED`,
            `ROLLING`, `STARTING` and `NETSTARTING`.
        position : jack_position_t
            See the `JACK transport documentation`__ for the available
            fields.

            __ https://jackaudio.org/api/structjack__position__t.html

        See Also
        --------
        transport_query, transport_reposition_struct

        """
        state = _lib.jack_transport_query(self._ptr, self._position)
        return state, self._position

    def transport_reposition_struct(self, position):
        """Request a new transport position.

        May be called at any time by any client.  The new position takes
        effect in two process cycles.  If there are slow-sync clients
        and the transport is already rolling, it will enter the
        `STARTING` state and begin invoking their sync callbacks
        (see `set_sync_callback()`) until ready.
        This function is realtime-safe.

        Parameters
        ----------
        position : jack_position_t
            Requested new transport position.  This is the same
            structure as returned by `transport_query_struct()`.

        See Also
        --------
        transport_query_struct, transport_locate

        """
        _check(_lib.jack_transport_reposition(self._ptr, position),
               'Error re-positioning transport')

    def set_sync_timeout(self, timeout):
        """Set the timeout value for slow-sync clients.

        This timeout prevents unresponsive slow-sync clients from
        completely halting the transport mechanism.  The default is two
        seconds.  When the timeout expires, the transport starts
        rolling, even if some slow-sync clients are still unready.
        The *sync callbacks* of these clients continue being invoked,
        giving them a chance to catch up.

        Parameters
        ----------
        timeout : int
            Delay (in microseconds) before the timeout expires.

        See Also
        --------
        set_sync_callback

        """
        _check(_lib.jack_set_sync_timeout(self._ptr, timeout),
               'Error setting sync timeout')

    def set_freewheel(self, onoff):
        """Start/Stop JACK's "freewheel" mode.

        When in "freewheel" mode, JACK no longer waits for any external
        event to begin the start of the next process cycle.

        As a result, freewheel mode causes "faster than realtime"
        execution of a JACK graph. If possessed, real-time scheduling is
        dropped when entering freewheel mode, and if appropriate it is
        reacquired when stopping.

        IMPORTANT: on systems using capabilities to provide real-time
        scheduling (i.e. Linux kernel 2.4), if onoff is zero, this
        function must be called from the thread that originally called
        `activate()`.  This restriction does not apply to other systems
        (e.g. Linux kernel 2.6 or OS X).

        Parameters
        ----------
        onoff : bool
            If ``True``, freewheel mode starts. Otherwise freewheel mode
            ends.

        See Also
        --------
        set_freewheel_callback

        """
        _check(_lib.jack_set_freewheel(self._ptr, onoff),
               'Error setting freewheel mode')

    def set_shutdown_callback(self, callback):
        """Register shutdown callback.

        Register a function (and optional argument) to be called if and
        when the JACK server shuts down the client thread.
        The function must be written as if it were an asynchonrous POSIX
        signal handler -- use only async-safe functions, and remember
        that it is executed from another thread.
        A typical function might set a flag or write to a pipe so that
        the rest of the application knows that the JACK client thread
        has shut down.

        .. note:: Clients do not need to call this.  It exists only to
           help more complex clients understand what is going on.  It
           should be called before `activate()`.

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever the JACK
            daemon is shutdown.  It must have this signature::

                callback(status: Status, reason: str) -> None

            The argument *status* is of type `jack.Status`.

            .. note:: The *callback* should typically signal another
               thread to correctly finish cleanup by calling `close()`
               (since it cannot be called directly in the context of the
               thread that calls the shutdown callback).

               After server shutdown, the client is *not* deallocated by
               JACK, the user (that's you!) is responsible to properly
               use `close()` to release client ressources.
               Alternatively, the `Client` object can be used as a
               *context manager* in a *with statement*, which takes care
               of activating, deactivating and closing the client
               automatically.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.

        """
        @self._callback('JackInfoShutdownCallback')
        def callback_wrapper(code, reason, _):
            callback(Status(code), _decode(reason))

        _lib.jack_on_info_shutdown(self._ptr, callback_wrapper, _ffi.NULL)

    def set_process_callback(self, callback):
        """Register process callback.

        Tell the JACK server to call *callback* whenever there is work
        be done.

        The code in the supplied function must be suitable for real-time
        execution.  That means that it cannot call functions that might
        block for a long time. This includes malloc, free, printf,
        pthread_mutex_lock, sleep, wait, poll, select, pthread_join,
        pthread_cond_wait, etc, etc.

        .. warning:: Most Python interpreters use a `global interpreter
           lock (GIL)`__, which violates the above real-time
           requirement.  Furthermore, Python's `garbage collector`__
           might become active at an inconvenient time and block the
           process callback for some time.

           Because of this, Python is not really suitable for real-time
           processing.  If you want to implement a *reliable* real-time
           audio/MIDI application, you should use a different
           programming language, such as C or C++.

           If you can live with some random audio drop-outs now and
           then, feel free to continue using Python!

        __ https://en.wikipedia.org/wiki/Global_Interpreter_Lock
        __ https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called by the engine anytime
            there is work to be done.  It must have this signature::

                callback(frames: int) -> None

            The argument *frames* specifies the number of frames that
            have to be processed in the current audio block.
            It will be the same number as `blocksize` and it will be a
            power of two.

            As long as the client is active, the *callback* will be
            called once in each process cycle.  However, if an exception
            is raised inside of a *callback*, it will not be called
            anymore.  The exception `CallbackExit` can be used to
            silently prevent further callback invocations, all other
            exceptions will print an error message to *stderr*.

        """
        @self._callback('JackProcessCallback', error=_FAILURE)
        def callback_wrapper(frames, _):
            try:
                callback(frames)
            except CallbackExit:
                return _FAILURE
            return _SUCCESS

        _check(_lib.jack_set_process_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting process callback')

    def set_freewheel_callback(self, callback):
        """Register freewheel callback.

        Tell the JACK server to call *callback* whenever we enter or
        leave "freewheel" mode.
        The argument to the callback will be ``True`` if JACK is
        entering freewheel mode, and ``False`` otherwise.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever JACK starts
            or stops freewheeling.  It must have this signature::

                callback(starting: bool) -> None

            The argument *starting* is ``True`` if we start to
            freewheel, ``False`` otherwise.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.

        See Also
        --------
        set_freewheel

        """
        @self._callback('JackFreewheelCallback')
        def callback_wrapper(starting, _):
            callback(bool(starting))

        _check(_lib.jack_set_freewheel_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting freewheel callback')

    def set_blocksize_callback(self, callback):
        """Register blocksize callback.

        Tell JACK to call *callback* whenever the size of the the buffer
        that will be passed to the process callback is about to change.
        Clients that depend on knowing the buffer size must supply a
        *callback* before activating themselves.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is invoked whenever the JACK
            engine buffer size changes.  It must have this signature::

                callback(blocksize: int) -> None

            The argument *blocksize* is the new buffer size.
            The *callback* is supposed to raise `CallbackExit` on error.

            .. note:: Although this function is called in the JACK
               process thread, the normal process cycle is suspended
               during its operation, causing a gap in the audio flow.
               So, the *callback* can allocate storage, touch memory not
               previously referenced, and perform other operations that
               are not realtime safe.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.

        See Also
        --------
        :attr:`blocksize`

        """
        @self._callback('JackBufferSizeCallback', error=_FAILURE)
        def callback_wrapper(blocksize, _):
            try:
                callback(blocksize)
            except CallbackExit:
                return _FAILURE
            return _SUCCESS

        _check(_lib.jack_set_buffer_size_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting blocksize callback')

    def set_samplerate_callback(self, callback):
        """Register samplerate callback.

        Tell the JACK server to call *callback* whenever the system
        sample rate changes.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called when the engine sample
            rate changes.  It must have this signature::

                callback(samplerate: int) -> None

            The argument *samplerate* is the new engine sample rate.
            The *callback* is supposed to raise `CallbackExit` on error.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.

        See Also
        --------
        :attr:`samplerate`

        """
        @self._callback('JackSampleRateCallback', error=_FAILURE)
        def callback_wrapper(samplerate, _):
            try:
                callback(samplerate)
            except CallbackExit:
                return _FAILURE
            return _SUCCESS

        _check(_lib.jack_set_sample_rate_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting samplerate callback')

    def set_client_registration_callback(self, callback):
        """Register client registration callback.

        Tell the JACK server to call *callback* whenever a client is
        registered or unregistered.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever a client is
            registered or unregistered.  It must have this signature::

                callback(name: str, register: bool) -> None

            The first argument contains the client name, the second
            argument is ``True`` if the client is being registered and
            ``False`` if the client is being unregistered.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.

        """
        @self._callback('JackClientRegistrationCallback')
        def callback_wrapper(name, register, _):
            callback(_decode(name), bool(register))

        _check(_lib.jack_set_client_registration_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting client registration callback')

    def set_port_registration_callback(self, callback=None,
                                       only_available=True):
        """Register port registration callback.

        Tell the JACK server to call *callback* whenever a port is
        registered or unregistered.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        .. note:: Due to JACK 1 behavior, it is not possible to get
           the pointer to an unregistering JACK Port if it already
           existed before `activate()` was called. This will cause
           the callback not to be called if *only_available* is
           ``True``, or called with ``None`` as first argument (see
           below).

           To avoid this, call `Client.get_ports()` just after
           `activate()`, allowing the module to store pointers to
           already existing ports and always receive a `Port`
           argument for this callback.

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever a port is
            registered or unregistered.  It must have this signature::

                callback(port: Port, register: bool) -> None

            The first argument is a `Port`, `MidiPort`, `OwnPort` or
            `OwnMidiPort` object, the second argument is ``True`` if the
            port is being registered, ``False`` if the port is being
            unregistered.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.
        only_available : bool, optional
            If ``True``, the *callback* is not called if the port in
            question is not available anymore (after another JACK client
            has unregistered it).
            If ``False``, it is called nonetheless, but the first
            argument of the *callback* will be ``None`` if the port is
            not available anymore.

        See Also
        --------
        Ports.register

        """
        if callback is None:
            return lambda cb: self.set_port_registration_callback(
                cb, only_available)

        @self._callback('JackPortRegistrationCallback')
        def callback_wrapper(port_id, register, _):
            port_ptr = _lib.jack_port_by_id(self._ptr, port_id)
            if port_ptr:
                port = self._wrap_port_ptr(port_ptr)
            elif only_available:
                return
            else:
                port = None
            callback(port, bool(register))

        _check(_lib.jack_set_port_registration_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting port registration callback')

    def set_port_connect_callback(self, callback=None, only_available=True):
        """Register port connect callback.

        Tell the JACK server to call *callback* whenever a port is
        connected or disconnected.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        .. note:: Due to JACK 1 behavior, it is not possible to get
           the pointer to an unregistering JACK Port if it already
           existed before `activate()` was called. This will cause
           the callback not to be called if *only_available* is
           ``True``, or called with ``None`` as first argument (see
           below).

           To avoid this, call `Client.get_ports()` just after
           `activate()`, allowing the module to store pointers to
           already existing ports and always receive a `Port`
           argument for this callback.

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever a port is
            connected or disconnected.  It must have this signature::

                callback(a: Port, b: Port, connect: bool) -> None

            The first and second arguments contain `Port`, `MidiPort`,
            `OwnPort` or `OwnMidiPort` objects of the ports which are
            connected or disconnected.  The third argument is ``True``
            if the ports were connected and ``False`` if the ports were
            disconnected.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.
        only_available : bool, optional
            See `set_port_registration_callback()`.
            If ``False``, the first and/or the second argument to the
            *callback* may be ``None``.

        See Also
        --------
        Client.connect, OwnPort.connect

        """
        if callback is None:
            return lambda cb: self.set_port_connect_callback(
                cb, only_available)

        @self._callback('JackPortConnectCallback')
        def callback_wrapper(a, b, connect, _):
            port_ids = a, b
            ports = [None, None]
            for idx in 0, 1:
                ptr = _lib.jack_port_by_id(self._ptr, port_ids[idx])
                if ptr:
                    ports[idx] = self._wrap_port_ptr(ptr)
                elif only_available:
                    return
                else:
                    pass  # Do nothing, port is already None
            callback(ports[0], ports[1], bool(connect))

        _check(_lib.jack_set_port_connect_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting port connect callback')

    def set_port_rename_callback(self, callback=None, only_available=True):
        """Register port rename callback.

        Tell the JACK server to call *callback* whenever a port is
        renamed.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever the port name
            has been changed.  It must have this signature::

                callback(port: Port, old: str, new: str) -> None

            The first argument is the port that has been renamed (a
            `Port`, `MidiPort`, `OwnPort` or `OwnMidiPort` object); the
            second and third argument is the old and new name,
            respectively.  The *callback* is supposed to raise
            `CallbackExit` on error.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.
        only_available : bool, optional
            See `set_port_registration_callback()`.

        See Also
        --------
        :attr:`Port.shortname`

        Notes
        -----
        The port rename callback is not available in JACK 1!
        See and `this commit message`__.

        __ https://github.com/jackaudio/jack1/commit/
           94c819accfab2612050e875c24cf325daa0fd26d

        """
        if callback is None:
            return lambda cb: self.set_port_rename_callback(cb, only_available)

        @self._callback('JackPortRenameCallback', error=_FAILURE)
        def callback_wrapper(port_id, old_name, new_name, _):
            port_ptr = _lib.jack_port_by_id(self._ptr, port_id)
            if port_ptr:
                port = self._wrap_port_ptr(port_ptr)
            elif only_available:
                return
            else:
                port = None
            try:
                callback(port, _decode(old_name), _decode(new_name))
            except CallbackExit:
                return _FAILURE
            return _SUCCESS

        _check(_lib.jack_set_port_rename_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting port rename callback')

    def set_graph_order_callback(self, callback):
        """Register graph order callback.

        Tell the JACK server to call *callback* whenever the processing
        graph is reordered.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever the
            processing graph is reordered.
            It must have this signature::

                callback() -> None

            The *callback* is supposed to raise `CallbackExit` on error.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.

        """
        @self._callback('JackGraphOrderCallback', error=_FAILURE)
        def callback_wrapper(_):
            try:
                callback()
            except CallbackExit:
                return _FAILURE
            return _SUCCESS

        _check(_lib.jack_set_graph_order_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting graph order callback')

    def set_xrun_callback(self, callback):
        """Register xrun callback.

        Tell the JACK server to call *callback* whenever there is an
        xrun.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: This function cannot be called while the client is
           activated (after `activate()` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever an xrun has
            occured.  It must have this signature::

                callback(delayed_usecs: float) -> None

            The callback argument is the delay in microseconds due to
            the most recent XRUN occurrence.
            The *callback* is supposed to raise `CallbackExit` on error.

            .. note:: Same as with most callbacks, no functions that
               interact with the JACK daemon should be used here.

        """
        @self._callback('JackXRunCallback', error=_FAILURE)
        def callback_wrapper(_):
            try:
                callback(_lib.jack_get_xrun_delayed_usecs(self._ptr))
            except CallbackExit:
                return _FAILURE
            return _SUCCESS

        _check(_lib.jack_set_xrun_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting xrun callback')

    def set_sync_callback(self, callback):
        """Register (or unregister) as a slow-sync client.

        A slow-sync client is one that cannot respond immediately to
        transport position changes.

        The *callback* will be invoked at the first available
        opportunity after its registration is complete.  If the client
        is currently active this will be the following process cycle,
        otherwise it will be the first cycle after calling `activate()`.
        After that, it runs whenever some client requests a new
        position, or the transport enters the `STARTING` state.
        While the client is active, this callback is invoked just before
        the *process callback* (see `set_process_callback()`) in the
        same thread.

        Clients that don't set a *sync callback* are assumed to be ready
        immediately any time the transport wants to start.

        Parameters
        ----------
        callback : callable or None

            User-supplied function that returns ``True`` when the
            slow-sync client is ready.  This realtime function must not
            wait.  It must have this signature::

                callback(state: int, pos: jack_position_t) -> bool

            The *state* argument will be:

            - `STOPPED` when a new position is requested;
            - `STARTING` when the transport is waiting to start;
            - `ROLLING` when the timeout has expired, and the position
              is now a moving target.

            The *pos* argument holds the new transport position using
            the same structure as returned by
            `transport_query_struct()`.

            Setting *callback* to ``None`` declares that this
            client no longer requires slow-sync processing.

        See Also
        --------
        set_sync_timeout

        """
        if callback is None:
            callback_wrapper = _ffi.NULL
        else:

            @self._callback('JackSyncCallback', error=False)
            def callback_wrapper(state, pos, _):
                return callback(state, pos)

        _check(
            _lib.jack_set_sync_callback(
                self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting sync callback')

    def release_timebase(self):
        """De-register as timebase master.

        Should be called by the current timebase master to release
        itself from that responsibility and to stop the callback
        registered with `set_timebase_callback()` from being called.

        If the timebase master releases the timebase or leaves the JACK
        graph for any reason, the JACK engine takes over at the start of
        the next process cycle. The transport state does not change. If
        rolling, it continues to play, with frame numbers as the only
        available position information.

        Raises
        ------
        JackError
            If the client is not the current timebase master or
            releasing the timebase failed for another reason

        See Also
        --------
        set_timebase_callback

        """
        _check(
            _lib.jack_release_timebase(self._ptr),
            'Error releasing timebase')

    def set_timebase_callback(self, callback=None, conditional=False):
        """Register as timebase master for the JACK subsystem.

        The timebase master registers a callback that updates extended
        position information such as beats or timecode whenever
        necessary.  Without this extended information, there is no need
        for this function.

        There is never more than one master at a time.  When a new
        client takes over, the former callback is no longer called.
        Taking over the timebase may be done conditionally, so that
        *callback* is not registered if there was a master already.

        Parameters
        ----------
        callback : callable
            Realtime function that returns extended position
            information.  Its output affects all of the following
            process cycle.  This realtime function must not wait.
            It is called immediately after the process callback (see
            `set_process_callback()`) in the same thread whenever the
            transport is rolling, or when any client has requested a new
            position in the previous cycle.  The first cycle after
            `set_timebase_callback()` is also treated as a new position,
            or the first cycle after `activate()` if the client had been
            inactive.  The *callback* must have this signature::

                callback(
                    state: int,
                    blocksize: int,
                    pos: jack_position_t,
                    new_pos: bool,
                ) -> None

            state
                The current transport state.  See `transport_state`.
            blocksize
                The number of frames in the current period.
                See `blocksize`.
            pos
                The position structure for the next cycle; ``pos.frame``
                will be its frame number.  If *new_pos* is ``False``,
                this structure contains extended position information
                from the current cycle.  If *new_pos* is ``True``, it
                contains whatever was set by the requester.
                The *callback*'s task is to update the extended
                information here.  See `transport_query_struct()`
                for details about ``jack_position_t``.
            new_pos
                ``True`` for a newly requested *pos*, or for the first
                cycle after the timebase callback is defined.

            .. note:: The *pos* argument must not be used to set
               ``pos.frame``.  To change position, use
               `transport_reposition_struct()` or `transport_locate()`.
               These functions are realtime-safe, the timebase callback
               can call them directly.
        conditional : bool
            Set to ``True`` for a conditional request.

        Returns
        -------
        bool
            ``True`` if the timebase callback was registered.
            ``False`` if a conditional request failed because another
            timebase master is already registered.

        """
        if callback is None:
            return lambda cb: self.set_timebase_callback(cb, conditional)

        @self._callback('JackTimebaseCallback')
        def callback_wrapper(state, blocksize, pos, new_pos, _):
            callback(state, blocksize, pos, bool(new_pos))

        err = _lib.jack_set_timebase_callback(self._ptr, conditional,
                                              callback_wrapper, _ffi.NULL)

        # Because of a bug in JACK2 version <= 1.9.10, we also check for -1.
        # See https://github.com/jackaudio/jack2/pull/123
        if conditional and err in (_errno.EBUSY, -1):
            return False
        _check(err, 'Error setting timebase callback')
        return True

    def set_property_change_callback(self, callback):
        """Register property change callback.

        Tell the JACK server to call *callback* whenever a property is
        created, changed or deleted.

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever a property is
            created, changed or deleted.  It must have this signature::

                callback(subject: int, key: str, change: int) -> None

            The first and second arguments are the *subject* and *key*,
            respectively.  See `set_property()` for details.
            The third argument has one of the values `PROPERTY_CREATED`,
            `PROPERTY_CHANGED` or `PROPERTY_DELETED`, which should be
            self-explanatory.

        """
        @self._callback('JackPropertyChangeCallback')
        def callback_wrapper(subject, key, change, _):
            callback(subject, _decode(key) if key else '', change)

        _check(_lib.jack_set_property_change_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            'Error setting property change callback')

    def get_uuid_for_client_name(self, name):
        """Get the session ID for a client name.

        The session manager needs this to reassociate a client name to
        the session ID.

        Raises
        ------
        JackError
            If no client with the given name exists.

        """
        uuid = _ffi.gc(_lib.jack_get_uuid_for_client_name(
            self._ptr, name.encode()), _lib.jack_free)
        if not uuid:
            raise JackError('Unable to get session ID for {0!r}'.format(name))
        return _decode(uuid)

    def get_client_name_by_uuid(self, uuid):
        """Get the client name for a session ID.

        In order to snapshot the graph connections, the session manager
        needs to map session IDs to client names.

        Raises
        ------
        JackError
            If no client with the given UUID exists.

        """
        name = _ffi.gc(_lib.jack_get_client_name_by_uuid(
            self._ptr, uuid.encode()), _lib.jack_free)
        if not name:
            raise JackError('Unable to get client name for {0!r}'.format(uuid))
        return _decode(name)

    def get_port_by_name(self, name):
        """Get port by name.

        Given a full port name, this returns a `Port`, `MidiPort`,
        `OwnPort` or `OwnMidiPort` object.

        Raises
        ------
        JackError
            If no port with the given name exists.

        """
        port_ptr = _lib.jack_port_by_name(self._ptr, name.encode())
        if not port_ptr:
            raise JackError('Port {0!r} not available'.format(name))
        return self._wrap_port_ptr(port_ptr)

    def get_all_connections(self, port):
        """Return a list of ports which the given port is connected to.

        This differs from `OwnPort.connections` (also available on
        `OwnMidiPort`) in two important respects:

        1) You may not call this function from code that is executed in
           response to a JACK event. For example, you cannot use it in a
           graph order callback.

        2) You need not be the owner of the port to get information
           about its connections.

        """
        port = self._get_port_ptr(port)
        names = _ffi.gc(_lib.jack_port_get_all_connections(self._ptr, port),
                        _lib.jack_free)
        return self._port_list_from_pointers(names)

    def get_ports(self, name_pattern='', is_audio=False, is_midi=False,
                  is_input=False, is_output=False, is_physical=False,
                  can_monitor=False, is_terminal=False):
        """Return a list of selected ports.

        Parameters
        ----------
        name_pattern : str
            A regular expression used to select ports by name.  If
            empty, no selection based on name will be carried out.
        is_audio, is_midi : bool
            Select audio/MIDI ports.  If neither of them is ``True``,
            both types of ports are selected.
        is_input, is_output, is_physical, can_monitor, is_terminal : bool
            Select ports by their flags.  If none of them are ``True``,
            no selection based on flags will be carried out.

        Returns
        -------
        list of Port/MidiPort/OwnPort/OwnMidiPort
            All ports that satisfy the given conditions.

        """
        if is_audio and not is_midi:
            type_pattern = _AUDIO
        elif is_midi and not is_audio:
            type_pattern = _MIDI
        else:
            type_pattern = b''
        flags = 0x0
        if is_input:
            flags |= _lib.JackPortIsInput
        if is_output:
            flags |= _lib.JackPortIsOutput
        if is_physical:
            flags |= _lib.JackPortIsPhysical
        if can_monitor:
            flags |= _lib.JackPortCanMonitor
        if is_terminal:
            flags |= _lib.JackPortIsTerminal
        names = _ffi.gc(_lib.jack_get_ports(
            self._ptr, name_pattern.encode(), type_pattern, flags),
            _lib.jack_free)
        return self._port_list_from_pointers(names)

    def set_property(self, subject, key, value, type=''):
        """Set a metadata property on *subject*.

        Parameters
        ----------
        subject : int or str
            The subject (UUID) to set the property on.
            UUIDs can be obtained with `Client.uuid`, `Port.uuid` and
            `Client.get_uuid_for_client_name()`.
        key : str
            The key (URI) of the property.  Some predefined keys are
            available as ``jack.METADATA_*`` module constants.
        value : str or bytes
            The value of the property.
        type : str, optional
            The type of the property, either a MIME type or URI.
            If *type* is empty, the *value* is assumed to be a UTF-8
            encoded string (``'text/plain'``).

            Example values:

            - ``'image/png;base64'`` (base64 encoded PNG image)
            - ``'http://www.w3.org/2001/XMLSchema#int'`` (integer)

            Official types are preferred, but clients may use any
            syntactically valid MIME type (which start with a type and
            slash, like ``'text/...'``).  If a URI type is used, it must
            be a complete absolute URI (which start with a scheme and
            colon, like ``'http:'``).

        See Also
        --------
        get_property
        get_properties
        get_all_properties
        remove_property
        remove_properties
        remove_all_properties
        set_property_change_callback

        """
        subject = _uuid_parse(subject)
        if isinstance(value, str):
            value = value.encode()
        if isinstance(type, str):
            type = type.encode()
        if _lib.jack_set_property(
                self._ptr, subject, key.encode(), value, type) != 0:
            raise ValueError('Unable to set property {!r} for subject {!r}'
                             .format(key, subject))

    def remove_property(self, subject, key):
        """Remove a single metadata property on *subject*.

        Parameters
        ----------
        subject : int or str
            The subject (UUID) to remove the property from.
            UUIDs can be obtained with `Client.uuid`, `Port.uuid` and
            `Client.get_uuid_for_client_name()`.
        key : str
            The key of the property to be removed.

        See Also
        --------
        set_property
        get_property
        get_properties
        get_all_properties
        remove_properties
        remove_all_properties
        set_property_change_callback

        """
        subject = _uuid_parse(subject)
        if _lib.jack_remove_property(self._ptr, subject, key.encode()) != 0:
            raise ValueError('Unable to remove property {!r} for subject {!r}'
                             .format(key, subject))

    def remove_properties(self, subject):
        """Remove all metadata properties on *subject*.

        Parameters
        ----------
        subject : int or str
            The subject (UUID) to remove all properties from.
            UUIDs can be obtained with `Client.uuid`, `Port.uuid` and
            `Client.get_uuid_for_client_name()`.

        Returns
        -------
        int
            The number of properties removed.

        See Also
        --------
        set_property
        get_property
        get_properties
        get_all_properties
        remove_property
        remove_all_properties
        set_property_change_callback

        """
        subject = _uuid_parse(subject)
        number = _lib.jack_remove_properties(self._ptr, subject)
        if number < 0:
            raise RuntimeError(
                'Unable to remove properties for subject {!r}'.format(subject))
        return number

    def remove_all_properties(self):
        """Remove all metadata properties.

        .. warning::

            This deletes all metadata managed by a running JACK server.
            Data lost cannot be recovered (though it can be recreated by
            new calls to `set_property()`).

        See Also
        --------
        set_property
        get_property
        get_properties
        get_all_properties
        remove_property
        remove_properties
        set_property_change_callback

        """
        if _lib.jack_remove_all_properties(self._ptr) != 0:
            raise RuntimeError('Unable to remove properties')

    def _callback(self, cdecl, **kwargs):
        """Wrapper for ffi.callback() that keeps callback alive."""
        def callback_decorator(python_callable):
            function_ptr = _ffi.callback(cdecl, python_callable, **kwargs)
            self._keepalive.append(function_ptr)
            return function_ptr
        return callback_decorator

    def _register_port(self, name, porttype, is_terminal, is_physical, flags):
        """Create a new port.

        Raises
        ------
        JackError
            If the port can not be registered, e.g. because the name is
            non-unique or too long.

        """
        if is_terminal:
            flags |= _lib.JackPortIsTerminal
        if is_physical:
            flags |= _lib.JackPortIsPhysical
        port_ptr = _lib.jack_port_register(self._ptr, name.encode(), porttype,
                                           flags, 0)
        if not port_ptr:
            raise JackError(
                '{0!r}: port registration failed'.format(name))
        return self._wrap_port_ptr(port_ptr)

    def _port_list_from_pointers(self, names):
        """Get list of Port objects from char**."""
        ports = []
        if names:
            idx = 0
            while True:
                name = names[idx]
                if not name:
                    break
                ports.append(self.get_port_by_name(_decode(name)))
                idx += 1
        return ports

    def _get_port_ptr(self, port):
        """Get port pointer from Port object or string or port pointer."""
        if isinstance(port, Port):
            port = port._ptr
        elif isinstance(port, str):
            port = self.get_port_by_name(port)._ptr
        return port

    def _wrap_port_ptr(self, ptr):
        """Create appropriate port object for a given port pointer."""
        porttype = _ffi.string(_lib.jack_port_type(ptr))
        if porttype == _AUDIO:
            cls = OwnPort if self.owns(ptr) else Port
        elif porttype == _MIDI:
            cls = OwnMidiPort if self.owns(ptr) else MidiPort
        else:
            assert False
        return cls(ptr, self)


class Port(object):
    """A JACK audio port.

    This class cannot be instantiated directly.  Instead, instances of
    this class are returned from `Client.get_port_by_name()`,
    `Client.get_ports()`, `Client.get_all_connections()` and
    `OwnPort.connections`.
    In addition, instances of this class are available in the callbacks
    which are set with `Client.set_port_registration_callback()`,
    `Client.set_port_connect_callback()` or
    `Client.set_port_rename_callback`.

    Note, however, that if the used `Client` owns the respective port,
    instances of `OwnPort` (instead of `Port`) will be created.  In case
    of MIDI ports, instances of `MidiPort` or `OwnMidiPort` are created.

    Besides being the type of non-owned JACK audio ports, this class
    also serves as base class for all other port classes (`OwnPort`,
    `MidiPort` and `OwnMidiPort`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of `Client.inports`,
    `Client.outports`, `Client.midi_inports` and `Client.midi_outports`.

    """

    def __init__(self, port_ptr, client):
        self._ptr = port_ptr
        self._client = client

    def __repr__(self):
        return "jack.{0.__class__.__name__}('{0.name}')".format(self)

    def __eq__(self, other):
        """Ports are equal if their underlying port pointers are."""
        return self._ptr == other._ptr

    def __ne__(self, other):
        """This should be implemented whenever __eq__() is implemented."""
        return not self.__eq__(other)

    @property
    def name(self):
        """Full name of the JACK port (read-only)."""
        return _decode(_lib.jack_port_name(self._ptr))

    @property
    def shortname(self):
        """Short name of the JACK port, not including the client name.

        Must be unique among all ports owned by a client.

        May be modified at any time.  If the resulting full name
        (including the ``client_name:`` prefix) is longer than
        `port_name_size()`, it will be truncated.

        """
        return _decode(_lib.jack_port_short_name(self._ptr))

    @shortname.setter
    def shortname(self, shortname):
        _check(_lib.jack_port_rename(self._client._ptr, self._ptr,
                                     shortname.encode()),
               'Error setting port name')

    @property
    def aliases(self):
        """Returns a list of strings with the aliases for the JACK port."""
        ctype = 'char[{}]'.format(_lib.jack_port_name_size())
        aliases = [_ffi.new(ctype), _ffi.new(ctype)]
        aliasesptr = _ffi.new('char *[]', aliases)
        result = []
        if _lib.jack_port_get_aliases(self._ptr, aliasesptr) > 0:
            for i in 0, 1:
                alias = _decode(aliases[i])
                if alias:
                    result.append(alias)

        return result

    def set_alias(self, alias):
        """Set an alias for the JACK port.

        Ports can have up to two aliases. If both are already set,
        this function will return an error.

        """
        _check(_lib.jack_port_set_alias(self._ptr, alias.encode()),
               'Error setting port alias')

    def unset_alias(self, alias):
        """Remove an alias for the JACK port.

        If the alias doesn't exist this function will return an error.

        """
        _check(_lib.jack_port_unset_alias(self._ptr, alias.encode()),
               'Error unsetting port alias')

    @property
    def uuid(self):
        """The UUID of the JACK port."""
        return _lib.jack_port_uuid(self._ptr)

    is_audio = property(lambda self: True, doc='This is always ``True``.')
    is_midi = property(lambda self: False, doc='This is always ``False``.')

    @property
    def is_input(self):
        """Can the port receive data?"""
        return self._hasflag(_lib.JackPortIsInput)

    @property
    def is_output(self):
        """Can data be read from this port?"""
        return self._hasflag(_lib.JackPortIsOutput)

    @property
    def is_physical(self):
        """Does it correspond to some kind of physical I/O connector?"""
        return self._hasflag(_lib.JackPortIsPhysical)

    @property
    def can_monitor(self):
        """Does a call to `request_monitor()` make sense?"""
        return self._hasflag(_lib.JackPortCanMonitor)

    @property
    def is_terminal(self):
        """Is the data consumed/generated?"""
        return self._hasflag(_lib.JackPortIsTerminal)

    def request_monitor(self, onoff):
        """Set input monitoring.

        If `can_monitor` is ``True``, turn input monitoring on or
        off.  Otherwise, do nothing.

        Parameters
        ----------
        onoff : bool
            If ``True``, switch monitoring on; if ``False``, switch it
            off.

        """
        _check(_lib.jack_port_request_monitor(self._ptr, onoff),
               'Unable to switch monitoring on/off')

    def _hasflag(self, flag):
        """Helper method for is_*()."""
        return bool(_lib.jack_port_flags(self._ptr) & flag)


class MidiPort(Port):
    """A JACK MIDI port.

    This class is derived from `Port` and has exactly the same
    attributes and methods.

    This class cannot be instantiated directly (see `Port`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of `Client.inports`,
    `Client.outports`, `Client.midi_inports` and `Client.midi_outports`.

    See Also
    --------
    Port, OwnMidiPort

    """

    is_audio = property(lambda self: False, doc='This is always ``False``.')
    is_midi = property(lambda self: True, doc='This is always ``True``.')


class OwnPort(Port):
    """A JACK audio port owned by a `Client`.

    This class is derived from `Port`.  `OwnPort` objects can do
    everything that `Port` objects can, plus a lot more.

    This class cannot be instantiated directly (see `Port`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of `Client.inports`,
    `Client.outports`, `Client.midi_inports` and `Client.midi_outports`.

    """

    @property
    def number_of_connections(self):
        """Number of connections to or from port."""
        return _lib.jack_port_connected(self._ptr)

    @property
    def connections(self):
        """List of ports which the port is connected to."""
        names = _ffi.gc(_lib.jack_port_get_connections(self._ptr),
                        _lib.jack_free)
        return self._client._port_list_from_pointers(names)

    def is_connected_to(self, port):
        """Am I *directly* connected to *port*?

        Parameters
        ----------
        port : str or Port
            Full port name or port object.

        """
        if isinstance(port, Port):
            port = port.name
        return bool(_lib.jack_port_connected_to(self._ptr, port.encode()))

    def connect(self, port):
        """Connect to given port.

        Parameters
        ----------
        port : str or Port
            Full port name or port object.

        See Also
        --------
        Client.connect

        """
        if not isinstance(port, Port):
            port = self._client.get_port_by_name(port)
        if self.is_output:
            source = self
            if not port.is_input:
                raise ValueError('Input port expected')
            destination = port
        elif self.is_input:
            destination = self
            if not port.is_output:
                raise ValueError('Output port expected')
            source = port
        else:
            assert False
        self._client.connect(source.name, destination.name)

    def disconnect(self, other=None):
        """Disconnect this port.

        Parameters
        ----------
        other : str or Port
            Port to disconnect from.
            By default, disconnect from all connected ports.

        """
        if other is None:
            _check(_lib.jack_port_disconnect(self._client._ptr, self._ptr),
                   'Error disconnecting {0!r}'.format(self.name))
        else:
            if self.is_output:
                args = self, other
            elif self.is_input:
                args = other, self
            self._client.disconnect(*args)

    def unregister(self):
        """Unregister port.

        Remove the port from the client, disconnecting any existing
        connections.  This also removes the port from
        `Client.inports`, `Client.outports`, `Client.midi_inports` or
        `Client.midi_outports`.

        """
        if self.is_audio:
            listname = ''
        elif self.is_midi:
            listname = 'midi_'
        if self.is_input:
            listname += 'inports'
        elif self.is_output:
            listname += 'outports'
        ports = getattr(self._client, listname)
        ports._portlist.remove(self)
        _check(_lib.jack_port_unregister(self._client._ptr, self._ptr),
               'Error unregistering {0!r}'.format(self.name))

    def get_buffer(self):
        """Get buffer for audio data.

        This returns a buffer holding the memory area associated with
        the specified port.  For an output port, it will be a memory
        area that can be written to; for an input port, it will be an
        area containing the data from the port's connection(s), or
        zero-filled.  If there are multiple inbound connections, the
        data will be mixed appropriately.

        Caching output ports is DEPRECATED in JACK 2.0, due to some new
        optimization (like "pipelining").  Port buffers have to be
        retrieved in each callback for proper functioning.

        This method shall only be called from within the process
        callback (see `Client.set_process_callback()`).

        """
        blocksize = self._client.blocksize
        return _ffi.buffer(_lib.jack_port_get_buffer(self._ptr, blocksize),
                           blocksize * _ffi.sizeof('float'))

    def get_array(self):
        """Get audio buffer as NumPy array.

        Make sure to ``import numpy`` before calling this, otherwise the
        first call might take a long time.

        This method shall only be called from within the process
        callback (see `Client.set_process_callback()`).

        See Also
        --------
        get_buffer

        """
        import numpy as np
        return np.frombuffer(self.get_buffer(), dtype=np.float32)


class OwnMidiPort(MidiPort, OwnPort):
    """A JACK MIDI port owned by a `Client`.

    This class is derived from `OwnPort` and `MidiPort`, which are
    themselves derived from `Port`.  It has the same attributes and
    methods as `OwnPort`, but `get_buffer()` and `get_array()` are
    disabled.  Instead, it has methods for sending and receiving MIDI
    events (to be used only from within the process callback -- see
    `Client.set_process_callback()`).

    This class cannot be instantiated directly (see `Port`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of `Client.inports`,
    `Client.outports`, `Client.midi_inports` and `Client.midi_outports`.

    """

    def __init__(self, *args, **kwargs):
        OwnPort.__init__(self, *args, **kwargs)
        self._event = _ffi.new('jack_midi_event_t*')

    def get_buffer(self):
        """Not available for MIDI ports."""
        raise NotImplementedError('get_buffer() not available on MIDI ports')

    def get_array(self):
        """Not available for MIDI ports."""
        raise NotImplementedError('get_array() not available on MIDI ports')

    @property
    def max_event_size(self):
        """Get the size of the largest event that can be stored by the port.

        This returns the current space available, taking into
        account events already stored in the port.

        """
        return _lib.jack_midi_max_event_size(
            _lib.jack_port_get_buffer(self._ptr, self._client.blocksize))

    @property
    def lost_midi_events(self):
        """Get the number of events that could not be written to the port.

        This being a non-zero value implies that the port is full.
        Currently the only way this can happen is if events are lost on
        port mixdown.

        """
        return _lib.jack_midi_get_lost_event_count(
            _lib.jack_port_get_buffer(self._ptr, self._client.blocksize))

    def incoming_midi_events(self):
        """Return generator for incoming MIDI events.

        JACK MIDI is normalised, the MIDI events yielded by this
        generator are guaranteed to be complete MIDI events (the status
        byte will always be present, and no realtime events will be
        interspersed with the events).

        Yields
        ------
        time : int
            Time (in samples) relative to the beginning of the current
            audio block.
        event : buffer
            The actual MIDI event data.

            .. warning:: The buffer is re-used (and therefore
               overwritten) between iterations.  If you want to keep the
               data beyond the current iteration, please make a copy.

        """
        event = self._event
        buf = _lib.jack_port_get_buffer(self._ptr, self._client.blocksize)
        for i in range(_lib.jack_midi_get_event_count(buf)):
            err = _lib.jack_midi_event_get(event, buf, i)
            if err:
                break
            yield event.time, _ffi.buffer(event.buffer, event.size)

    def clear_buffer(self):
        """Clear an event buffer.

        This should be called at the beginning of each process cycle
        before calling `reserve_midi_event()` or `write_midi_event()`.
        This function may not be called on an input port.

        """
        _lib.jack_midi_clear_buffer(
            _lib.jack_port_get_buffer(self._ptr, self._client.blocksize))

    def write_midi_event(self, time, event):
        """Create an outgoing MIDI event.

        Clients must write normalised MIDI data to the port - no running
        status and no (one-byte) realtime messages interspersed with
        other messages (realtime messages are fine when they occur on
        their own, like other messages).

        Events must be written in order, sorted by their sample offsets.
        JACK will not sort the events for you, and will refuse to store
        out-of-order events.

        Parameters
        ----------
        time : int
            Time (in samples) relative to the beginning of the current
            audio block.
        event : bytes or buffer or sequence of int
            The actual MIDI event data.

            .. note:: Buffer objects are only supported for CFFI >= 0.9.

        Raises
        ------
        JackError
            If MIDI event couldn't be written.

        """
        try:
            event = _ffi.from_buffer(event)
        except AttributeError:
            pass  # from_buffer() not supported
        except TypeError:
            pass  # input is not a buffer
        _check(_lib.jack_midi_event_write(
            _lib.jack_port_get_buffer(self._ptr, self._client.blocksize),
            time, event, len(event)), 'Error writing MIDI event')

    def reserve_midi_event(self, time, size):
        """Get a buffer where an outgoing MIDI event can be written to.

        Clients must write normalised MIDI data to the port - no running
        status and no (one-byte) realtime messages interspersed with
        other messages (realtime messages are fine when they occur on
        their own, like other messages).

        Events must be written in order, sorted by their sample offsets.
        JACK will not sort the events for you, and will refuse to store
        out-of-order events.

        Parameters
        ----------
        time : int
            Time (in samples) relative to the beginning of the current
            audio block.
        size : int
            Number of bytes to reserve.

        Returns
        -------
        buffer
            A buffer object where MIDI data bytes can be written to.
            If no space could be reserved, an empty buffer is returned.

        """
        buf = _lib.jack_midi_event_reserve(
            _lib.jack_port_get_buffer(self._ptr, self._client.blocksize),
            time, size)
        return _ffi.buffer(buf, size if buf else 0)


class Ports(object):
    """A list of input/output ports.

    This class is not meant to be instantiated directly.  It is only
    used as `Client.inports`, `Client.outports`, `Client.midi_inports`
    and `Client.midi_outports`.

    The ports can be accessed by indexing or by iteration.

    New ports can be added with `register()`, existing ports can be
    removed by calling their :meth:`~OwnPort.unregister` method.

    """

    def __init__(self, client, porttype, flag):
        self._client = client
        self._type = porttype
        self._flag = flag
        self._portlist = []

    def __len__(self):
        return self._portlist.__len__()

    def __getitem__(self, name):
        return self._portlist.__getitem__(name)

    # No __setitem__!

    def __iter__(self):
        return self._portlist.__iter__()

    def __repr__(self):
        return self._portlist.__repr__()

    def register(self, shortname, is_terminal=False, is_physical=False):
        """Create a new input/output port.

        The new `OwnPort` or `OwnMidiPort` object is automatically added
        to `Client.inports`, `Client.outports`, `Client.midi_inports` or
        `Client.midi_outports`.

        Parameters
        ----------
        shortname : str
            Each port has a short name.  The port's full name contains
            the name of the client concatenated with a colon (:)
            followed by its short name.  The `port_name_size()` is the
            maximum length of this full name.  Exceeding that will cause
            the port registration to fail.

            The port name must be unique among all ports owned by this
            client.
            If the name is not unique, the registration will fail.
        is_terminal : bool
            For an input port: If ``True``, the data received by the
            port will not be passed on or made available at any other
            port.
            For an output port: If ``True``, the data available at the
            port does not originate from any other port

            Audio synthesizers, I/O hardware interface clients, HDR
            systems are examples of clients that would set this flag for
            their ports.
        is_physical : bool
            If ``True`` the port corresponds to some kind of physical
            I/O connector.

        Returns
        -------
        Port
            A new `OwnPort` or `OwnMidiPort` instance.

        """
        port = self._client._register_port(
            shortname, self._type, is_terminal, is_physical, self._flag)
        self._portlist.append(port)
        return port

    def clear(self):
        """Unregister all ports in the list.

        See Also
        --------
        OwnPort.unregister

        """
        while self._portlist:
            self._portlist[0].unregister()


class RingBuffer(object):
    """JACK's lock-free ringbuffer."""

    def __init__(self, size):
        """Create a lock-free ringbuffer.

        A ringbuffer is a good way to pass data between threads
        (e.g. between the main program and the process callback),
        when streaming realtime data to slower media, like audio file
        playback or recording.

        The key attribute of a ringbuffer is that it can be safely
        accessed by two threads simultaneously -- one reading from the
        buffer and the other writing to it -- without using any
        synchronization or mutual exclusion primitives.  For this to
        work correctly, there can only be a single reader and a single
        writer thread.  Their identities cannot be interchanged.

        Parameters
        ----------
        size : int
            Size in bytes.  JACK will allocate a buffer of at least this
            size (rounded up to the next power of 2), but one byte is
            reserved for internal use.  Use `write_space` to
            determine the actual size available for writing.


        Raises
        ------
        JackError
            If the rightbufefr could not be allocated.

        """
        ptr = _lib.jack_ringbuffer_create(size)
        if not ptr:
            raise JackError('Could not create RingBuffer')
        self._ptr = _ffi.gc(ptr, _lib.jack_ringbuffer_free)

    @property
    def write_space(self):
        """The number of bytes available for writing."""
        return _lib.jack_ringbuffer_write_space(self._ptr)

    def write(self, data):
        """Write data into the ringbuffer.

        Parameters
        ----------
        data : buffer or bytes or iterable of int
            Bytes to be written to the ringbuffer.

        Returns
        -------
        int
            The number of bytes written, which could be less than the
            length of *data* if there was no more space left
            (see `write_space`).

        See Also
        --------
        :attr:`write_space`, :attr:`write_buffers`

        """
        try:
            data = _ffi.from_buffer(data)
        except AttributeError:
            pass  # from_buffer() not supported
        except TypeError:
            pass  # input is not a buffer
        return _lib.jack_ringbuffer_write(self._ptr, data, len(data))

    @property
    def write_buffers(self):
        """Contains two buffer objects that can be written to directly.

        Two are needed because the space available for writing may be
        split across the end of the ringbuffer.  Either of them could be
        0 length.

        This can be used as a no-copy version of `write()`.

        When finished with writing, `write_advance()` should be used.

        .. note:: After an operation that changes the write pointer
           (`write()`, `write_advance()`, `reset()`), the buffers are no
           longer valid and one should use this property again to get
           new ones.

        """
        vectors = _ffi.new('jack_ringbuffer_data_t[2]')
        _lib.jack_ringbuffer_get_write_vector(self._ptr, vectors)
        return (
            _ffi.buffer(vectors[0].buf, vectors[0].len),
            _ffi.buffer(vectors[1].buf, vectors[1].len)
        )

    def write_advance(self, size):
        """Advance the write pointer.

        After data has been written to the ringbuffer using
        `write_buffers`, use this method to advance the buffer pointer,
        making the data available for future read operations.

        Parameters
        ----------
        size : int
            The number of bytes to advance.

        """
        _lib.jack_ringbuffer_write_advance(self._ptr, size)

    @property
    def read_space(self):
        """The number of bytes available for reading."""
        return _lib.jack_ringbuffer_read_space(self._ptr)

    def read(self, size):
        """Read data from the ringbuffer.

        Parameters
        ----------
        size : int
            Number of bytes to read.

        Returns
        -------
        buffer
            A buffer object containing the requested data.
            If no more data is left (see `read_space`), a smaller
            (or even empty) buffer is returned.

        See Also
        --------
        peek, :attr:`read_space`, :attr:`read_buffers`

        """
        data = _ffi.new('unsigned char[]', size)
        size = _lib.jack_ringbuffer_read(self._ptr, data, size)
        return _ffi.buffer(data, size)

    def peek(self, size):
        """Peek at data from the ringbuffer.

        Opposed to `read()` this function does not move the read
        pointer.  Thus it's a convenient way to inspect data in the
        ringbuffer in a continuous fashion.
        The price is that the data is copied into a newly allocated
        buffer.  For "raw" non-copy inspection of the data in the
        ringbuffer use `read_buffers`.

        Parameters
        ----------
        size : int
            Number of bytes to peek.

        Returns
        -------
        buffer
            A buffer object containing the requested data.
            If no more data is left (see `read_space`), a smaller
            (or even empty) buffer is returned.

        See Also
        --------
        read, :attr:`read_space`, :attr:`read_buffers`

        """
        data = _ffi.new('unsigned char[]', size)
        size = _lib.jack_ringbuffer_peek(self._ptr, data, size)
        return _ffi.buffer(data, size)

    @property
    def read_buffers(self):
        """Contains two buffer objects that can be read directly.

        Two are needed because the data to be read may be split across
        the end of the ringbuffer.  Either of them could be 0 length.

        This can be used as a no-copy version of `peek()` or `read()`.

        When finished with reading, `read_advance()` should be used.

        .. note:: After an operation that changes the read pointer
           (`read()`, `read_advance()`, `reset()`), the buffers are no
           longer valid and one should use this property again to get
           new ones.

        """
        vectors = _ffi.new('jack_ringbuffer_data_t[2]')
        _lib.jack_ringbuffer_get_read_vector(self._ptr, vectors)
        return (
            _ffi.buffer(vectors[0].buf, vectors[0].len),
            _ffi.buffer(vectors[1].buf, vectors[1].len)
        )

    def read_advance(self, size):
        """Advance the read pointer.

        After data has been read from the ringbuffer using
        `read_buffers` or `peek()`, use this method to advance the
        buffer pointers, making that space available for future write
        operations.

        Parameters
        ----------
        size : int
            The number of bytes to advance.

        """
        _lib.jack_ringbuffer_read_advance(self._ptr, size)

    def mlock(self):
        """Lock a ringbuffer data block into memory.

        Uses the ``mlock()`` system call.  This prevents the
        ringbuffer's memory from being paged to the swap area.

        .. note:: This is not a realtime operation.

        """
        _check(_lib.jack_ringbuffer_mlock(self._ptr),
               'Error mlocking the RingBuffer data')

    def reset(self, size=None):
        """Reset the read and write pointers, making an empty buffer.

        .. note:: This is not thread safe.

        Parameters
        ----------
        size : int, optional
            The new size for the ringbuffer.
            Must be less than allocated size.

        """
        if size is None:
            _lib.jack_ringbuffer_reset(self._ptr)
        else:
            _lib.jack_ringbuffer_reset_size(self._ptr, size)

    @property
    def size(self):
        """The number of bytes in total used by the buffer.

        See Also
        --------
        :attr:`read_space`, :attr:`write_space`

        """
        return self._ptr.size


class Status(object):
    """Representation of the JACK status bits."""

    __slots__ = '_code'

    def __init__(self, code):
        self._code = code

    def __repr__(self):
        flags = ', '.join(name for name in dir(self)
                          if not name.startswith('_') and getattr(self, name))
        if not flags:
            flags = 'no flags set'
        return '<jack.Status 0x{0:X}: {1}>'.format(self._code, flags)

    @property
    def failure(self):
        """Overall operation failed."""
        return self._hasflag(_lib.JackFailure)

    @property
    def invalid_option(self):
        """The operation contained an invalid or unsupported option."""
        return self._hasflag(_lib.JackInvalidOption)

    @property
    def name_not_unique(self):
        """The desired client name was not unique.

        With the *use_exact_name* option of `Client`, this situation is
        fatal.  Otherwise, the name is modified by appending a dash and
        a two-digit number in the range "-01" to "-99".  `Client.name`
        will return the exact string that was used.  If the specified
        *name* plus these extra characters would be too long, the open
        fails instead.

        """
        return self._hasflag(_lib.JackNameNotUnique)

    @property
    def server_started(self):
        """The JACK server was started for this `Client`.

        Otherwise, it was running already.

        """
        return self._hasflag(_lib.JackServerStarted)

    @property
    def server_failed(self):
        """Unable to connect to the JACK server."""
        return self._hasflag(_lib.JackServerFailed)

    @property
    def server_error(self):
        """Communication error with the JACK server."""
        return self._hasflag(_lib.JackServerError)

    @property
    def no_such_client(self):
        """Requested client does not exist."""
        return self._hasflag(_lib.JackNoSuchClient)

    @property
    def load_failure(self):
        """Unable to load internal client."""
        return self._hasflag(_lib.JackLoadFailure)

    @property
    def init_failure(self):
        """Unable to initialize client."""
        return self._hasflag(_lib.JackInitFailure)

    @property
    def shm_failure(self):
        """Unable to access shared memory."""
        return self._hasflag(_lib.JackShmFailure)

    @property
    def version_error(self):
        """Client's protocol version does not match."""
        return self._hasflag(_lib.JackVersionError)

    @property
    def backend_error(self):
        """Backend error."""
        return self._hasflag(_lib.JackBackendError)

    @property
    def client_zombie(self):
        """Client zombified failure."""
        return self._hasflag(_lib.JackClientZombie)

    def _hasflag(self, flag):
        """Helper function for Status properties."""
        return bool(self._code & flag)


class TransportState(object):
    """Representation of the JACK transport state.

    See Also
    --------
    `Client.transport_state`, :meth:`Client.transport_query`

    """

    __slots__ = '_code'

    def __init__(self, code):
        self._code = code

    def __eq__(self, other):
        return self._code == other

    def __hash__(self):
        return hash(self._code)

    def __repr__(self):
        return 'jack.' + {
            _lib.JackTransportStopped: 'STOPPED',
            _lib.JackTransportRolling: 'ROLLING',
            _lib.JackTransportStarting: 'STARTING',
            _lib.JackTransportNetStarting: 'NETSTARTING',
        }[self._code]



class CallbackExit(Exception):
    """To be raised in a callback function to signal failure.

    See Also
    --------
    :meth:`Client.set_process_callback`
    :meth:`Client.set_blocksize_callback`
    :meth:`Client.set_samplerate_callback`
    :meth:`Client.set_port_rename_callback`
    :meth:`Client.set_graph_order_callback`
    :meth:`Client.set_xrun_callback`

    """

    pass


def _uuid_parse(uuid):
    if isinstance(uuid, (Client, Port)):
        uuid = uuid.uuid

    if isinstance(uuid, int):
        return uuid
    elif isinstance(uuid, str):
        uuid_ptr = _ffi.new('jack_uuid_t*')
        if _lib.jack_uuid_parse(uuid.encode(), uuid_ptr) != 0:
            raise ValueError('Unable to parse UUID: {!r}'.format(uuid))
        return uuid_ptr[0]
    raise TypeError('Invalid UUID: {!r}'.format(uuid))


def _description_to_dict(desc):
    assert desc != _ffi.NULL
    prop_dict = {}
    for i in range(desc.property_cnt):
        prop = desc.properties[i]
        key = _decode(prop.key)
        prop_dict[key] = (
            _ffi.string(prop.data),
            _decode(prop.type) if prop.type else '')
    free_description_itself = 0
    _lib.jack_free_description(desc, free_description_itself)
    return prop_dict


def get_property(subject, key):
    """Get a metadata property on *subject*.

    Parameters
    ----------
    subject : int or str
        The subject (UUID) to get the property from.
        UUIDs can be obtained with `Client.uuid`, `Port.uuid` and
        `Client.get_uuid_for_client_name()`.
    key : str
        The key of the property.

    Returns
    -------
    (bytes, str) or None
        A tuple containing the value of the property and the type of the
        property.  If *subject* doesn't have the property *key*,
        ``None`` is returned.

    See Also
    --------
    Client.set_property
    get_properties
    get_all_properties
    Client.remove_property
    Client.remove_properties
    Client.remove_all_properties
    Client.set_property_change_callback

    """
    subject = _uuid_parse(subject)
    data = _ffi.new('char**')
    type = _ffi.new('char**')
    if _lib.jack_get_property(subject, key.encode(), data, type) != 0:
        return None
    data = _ffi.gc(data[0], _lib.jack_free)
    type = _ffi.gc(type[0], _lib.jack_free)
    return _ffi.string(data), _decode(type) if type else ''


def get_properties(subject):
    """Get all metadata properties of *subject*.

    Parameters
    ----------
    subject : int or str
        The subject (UUID) to get all properties of.
        UUIDs can be obtained with `Client.uuid`, `Port.uuid` and
        `Client.get_uuid_for_client_name()`.

    Returns
    -------
    dict
        A dictionary mapping property names to ``(value, type)`` tuples.

    See Also
    --------
    Client.set_property
    get_property
    get_all_properties
    Client.remove_property
    Client.remove_properties
    Client.remove_all_properties
    Client.set_property_change_callback

    """
    subject = _uuid_parse(subject)
    desc = _ffi.new('jack_description_t*')
    number = _lib.jack_get_properties(subject, desc)
    if number < 0:
        raise RuntimeError(
            'Unable to get properties for subject {!r}'.format(subject))
    assert number == desc.property_cnt
    return _description_to_dict(desc)


def get_all_properties():
    """Get all properties for all subjects with metadata.

    Returns
    -------
    dict
        A dictionary mapping UUIDs to nested dictionaries as returned by
        `get_properties()`.

    See Also
    --------
    Client.set_property
    get_property
    get_properties
    Client.remove_property
    Client.remove_properties
    Client.remove_all_properties
    Client.set_property_change_callback

    """
    descs = _ffi.new('jack_description_t**')
    number = _lib.jack_get_all_properties(descs)
    if number < 0:
        raise RuntimeError('Error getting all properties')
    descs = _ffi.gc(descs[0], _lib.jack_free)
    prop_dict = {}
    for idx in range(number):
        desc = descs + idx
        assert desc.subject not in prop_dict
        prop_dict[desc.subject] = _description_to_dict(desc)
    return prop_dict


def position2dict(pos):
    """Convert CFFI position struct to a dict."""
    assert pos.unique_1 == pos.unique_2

    keys = ['usecs', 'frame_rate', 'frame']
    if pos.valid & _lib.JackPositionBBT:
        keys += ['bar', 'beat', 'tick', 'bar_start_tick', 'beats_per_bar',
                 'beat_type', 'ticks_per_beat', 'beats_per_minute']
    if pos.valid & _lib.JackPositionTimecode:
        keys += ['frame_time', 'next_time']
    if pos.valid & _lib.JackBBTFrameOffset:
        keys += ['bbt_offset']
    if pos.valid & _lib.JackAudioVideoRatio:
        keys += ['audio_frames_per_video_frame']
    if pos.valid & _lib.JackVideoFrameOffset:
        keys += ['video_offset']

    return dict((k, getattr(pos, k)) for k in keys)


def version():
    """Get tuple of major/minor/micro/protocol version."""
    v = _ffi.new('int[4]')
    _lib.jack_get_version(v+0, v+1, v+2, v+3)
    return tuple(v)


def version_string():
    """Get human-readable JACK version."""
    return _decode(_lib.jack_get_version_string())


def client_name_size():
    """Return the maximum number of characters in a JACK client name.

    This includes the final NULL character.  This value is a constant.

    """
    return _lib.jack_client_name_size()


def port_name_size():
    """Maximum length of port names.

    The maximum number of characters in a full JACK port name including
    the final NULL character.  This value is a constant.

    A port's full name contains the owning client name concatenated with
    a colon (:) followed by its short name and a NULL character.

    """
    return _lib.jack_port_name_size()


def set_error_function(callback=None):
    """Set the callback for error message display.

    Set it to ``None`` to restore the default error callback function
    (which prints the error message plus a newline to stderr).
    The *callback* function must have this signature::

        callback(message: str) -> None

    """
    _set_error_or_info_function(callback, _lib.jack_set_error_function)


def set_info_function(callback=None):
    """Set the callback for info message display.

    Set it to ``None`` to restore default info callback function
    (which prints the info message plus a newline to stderr).
    The *callback* function must have this signature::

        callback(message: str) -> None

    """
    _set_error_or_info_function(callback, _lib.jack_set_info_function)


def client_pid(name):
    """Return PID of a JACK client.

    Parameters
    ----------
    name : str
        Name of the JACK client whose PID shall be returned.

    Returns
    -------
    int
        PID of *name*.  If not available, 0 will be returned.

    """
    return _lib.jack_get_client_pid(name.encode())


def _set_error_or_info_function(callback, setter):
    """Helper for set_error_function() and set_info_function()."""
    if callback is None:
        callback_wrapper = _ffi.NULL
    else:
        @_ffi.callback('void (*)(const char*)')
        def callback_wrapper(msg):
            callback(_decode(msg))

        _keepalive[setter] = callback_wrapper
    setter(callback_wrapper)


_keepalive = {}


def _check(error_code, msg):
    """Check error code and raise JackError if non-zero."""
    if error_code:
        raise JackErrorCode(msg, error_code)
