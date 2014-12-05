# Copyright (c) 2014 Matthias Geier
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

http://jackclient-python.rtfd.org/

"""
__version__ = "0.1.0"

from cffi import FFI as _FFI

_ffi = _FFI()
_ffi.cdef("""

/* types.h */

typedef uint64_t jack_uuid_t;
typedef uint32_t jack_nframes_t;
/* TODO: jack_time_t */
typedef struct _jack_port jack_port_t;
typedef struct _jack_client jack_client_t;
typedef uint32_t jack_port_id_t;
typedef uint32_t jack_port_type_id_t;
enum JackOptions {
    JackNullOption = 0x00,
    JackNoStartServer = 0x01,
    JackUseExactName = 0x02,
    JackServerName = 0x04,
    JackLoadName = 0x08,
    JackLoadInit = 0x10,
    JackSessionID = 0x20
};
typedef enum JackOptions jack_options_t;
enum JackStatus {
    JackFailure = 0x01,
    JackInvalidOption = 0x02,
    JackNameNotUnique = 0x04,
    JackServerStarted = 0x08,
    JackServerFailed = 0x10,
    JackServerError = 0x20,
    JackNoSuchClient = 0x40,
    JackLoadFailure = 0x80,
    JackInitFailure = 0x100,
    JackShmFailure = 0x200,
    JackVersionError = 0x400,
    JackBackendError = 0x800,
    JackClientZombie = 0x1000
};
typedef enum JackStatus jack_status_t;
typedef int (*JackProcessCallback)(jack_nframes_t nframes, void* arg);
typedef int (*JackGraphOrderCallback)(void* arg);
typedef int (*JackXRunCallback)(void* arg);
typedef int (*JackBufferSizeCallback)(jack_nframes_t nframes, void* arg);
typedef int (*JackSampleRateCallback)(jack_nframes_t nframes, void* arg);
typedef void (*JackPortRegistrationCallback)(jack_port_id_t port, int /* register */, void* arg);
typedef void (*JackClientRegistrationCallback)(const char* name, int /* register */, void* arg);
typedef void (*JackPortConnectCallback)(jack_port_id_t a, jack_port_id_t b, int connect, void* arg);
typedef int (*JackPortRenameCallback)(jack_port_id_t port, const char* old_name, const char* new_name, void* arg);
typedef void (*JackFreewheelCallback)(int starting, void* arg);
/* not implemented: JackShutdownCallback */
typedef void (*JackInfoShutdownCallback)(jack_status_t code, const char* reason, void* arg);
/* hardcoded: JACK_DEFAULT_AUDIO_TYPE, jack_default_audio_sample_t */
enum JackPortFlags {
    JackPortIsInput = 0x1,
    JackPortIsOutput = 0x2,
    JackPortIsPhysical = 0x4,
    JackPortCanMonitor = 0x8,
    JackPortIsTerminal = 0x10,
};
typedef enum {
    JackTransportStopped = 0,
    JackTransportRolling = 1,
    JackTransportLooping = 2,
    JackTransportStarting = 3,
    JackTransportNetStarting = 4,
} jack_transport_state_t;
typedef struct _jack_position jack_position_t;

/* jack.h */

void jack_get_version(int* major_ptr, int* minor_ptr, int* micro_ptr, int* proto_ptr);
const char* jack_get_version_string();
jack_client_t* jack_client_open(const char* client_name, jack_options_t options, jack_status_t* status, ...);
/* deprecated: jack_client_new */
int jack_client_close(jack_client_t* client);
int jack_client_name_size(void);
char* jack_get_client_name(jack_client_t* client);
char* jack_get_uuid_for_client_name(jack_client_t* client, const char* client_name);
char* jack_get_client_name_by_uuid(jack_client_t* client, const char* client_uuid);
/* deprecated: jack_internal_client_new */
/* deprecated: jack_internal_client_close */
int jack_activate(jack_client_t* client);
int jack_deactivate(jack_client_t* client);
int jack_get_client_pid(const char* name);
/* not implemented: jack_client_thread_id */
int jack_is_realtime(jack_client_t* client);
/* not implemented (and deprecated): jack_thread_wait */
/* not implemented: jack_cycle_wait */
/* not implemented: jack_cycle_signal */
/* not implemented: jack_set_process_thread */
/* not implemented: jack_set_thread_init_callback */
/* not implemented (jack_on_info_shutdown is used): jack_on_shutdown */
void jack_on_info_shutdown(jack_client_t* client, JackInfoShutdownCallback shutdown_callback, void* arg);
int jack_set_process_callback(jack_client_t* client, JackProcessCallback process_callback, void* arg);
int jack_set_freewheel_callback(jack_client_t* client, JackFreewheelCallback freewheel_callback, void* arg);
int jack_set_buffer_size_callback(jack_client_t* client, JackBufferSizeCallback bufsize_callback, void* arg);
int jack_set_sample_rate_callback(jack_client_t* client, JackSampleRateCallback srate_callback, void* arg);
int jack_set_client_registration_callback(jack_client_t* client, JackClientRegistrationCallback registration_callback, void* arg);
int jack_set_port_registration_callback(jack_client_t* client, JackPortRegistrationCallback registration_callback, void* arg);
int jack_set_port_connect_callback(jack_client_t* client, JackPortConnectCallback connect_callback, void* arg);
int jack_set_port_rename_callback(jack_client_t* client, JackPortRenameCallback rename_callback, void* arg);
int jack_set_graph_order_callback(jack_client_t* client, JackGraphOrderCallback graph_callback, void*);
int jack_set_xrun_callback(jack_client_t* client, JackXRunCallback xrun_callback, void* arg);
/* TODO: jack_set_latency_callback */
int jack_set_freewheel(jack_client_t* client, int onoff);
int jack_set_buffer_size(jack_client_t* client, jack_nframes_t nframes);
jack_nframes_t jack_get_sample_rate(jack_client_t*);
jack_nframes_t jack_get_buffer_size(jack_client_t*);
/* deprecated: jack_engine_takeover_timebase() */
float jack_cpu_load(jack_client_t* client);
jack_port_t* jack_port_register(jack_client_t* client, const char* port_name, const char* port_type, unsigned long flags, unsigned long buffer_size);
int jack_port_unregister(jack_client_t* client, jack_port_t* port);
void* jack_port_get_buffer(jack_port_t* port, jack_nframes_t);
jack_uuid_t jack_port_uuid(const jack_port_t* port);
const char* jack_port_name(const jack_port_t* port);
const char* jack_port_short_name(const jack_port_t* port);
int jack_port_flags(const jack_port_t* port);
const char* jack_port_type(const jack_port_t* port);
jack_port_type_id_t jack_port_type_id(const jack_port_t* port);
int jack_port_is_mine(const jack_client_t* client, const jack_port_t* port);
int jack_port_connected(const jack_port_t* port);
int jack_port_connected_to(const jack_port_t* port, const char* port_name);
const char** jack_port_get_connections(const jack_port_t* port);
const char** jack_port_get_all_connections(const jack_client_t* client, const jack_port_t* port);
/* deprecated: jack_port_tie */
/* deprecated: jack_port_untie */
int jack_port_set_name(jack_port_t* port, const char* port_name);
/* TODO: jack_port_set_alias */
/* TODO: jack_port_unset_alias */
/* TODO: jack_port_get_aliases */
int jack_port_request_monitor(jack_port_t *port, int onoff);
/* not implemented (use jack_port_request_monitor): jack_port_request_monitor_by_name */
/* TODO: jack_port_ensure_monitor */
/* TODO: jack_port_monitoring_input */
int jack_connect(jack_client_t* client, const char* source_port, const char* destination_port);
int jack_disconnect(jack_client_t* client, const char* source_port, const char* destination_port);
int jack_port_disconnect(jack_client_t* client, jack_port_t* port);
int jack_port_name_size(void);
/* not implemented: jack_port_type_size */
/* not implemented: jack_port_type_get_buffer_size */
/* TODO: jack_port_set_latency */
/* TODO: jack_port_get_latency_range */
/* TODO: jack_port_set_latency_range */
/* TODO: jack_recompute_total_latencies */
/* TODO: jack_port_get_latency */
/* TODO: jack_port_get_total_latency */
/* TODO: jack_recompute_total_latency */
const char** jack_get_ports(jack_client_t* client, const char* port_name_pattern, const char* type_name_pattern, unsigned long flags);
jack_port_t* jack_port_by_name(jack_client_t* client, const char* port_name);
jack_port_t* jack_port_by_id(jack_client_t* client, jack_port_id_t port_id);
jack_nframes_t jack_frames_since_cycle_start(const jack_client_t*);
jack_nframes_t jack_frame_time(const jack_client_t*);
jack_nframes_t jack_last_frame_time(const jack_client_t* client);
/* TODO: jack_get_cycle_times */
/* TODO: jack_frames_to_time */
/* TODO: jack_time_to_frames */
/* TODO: jack_get_time */
void jack_set_error_function(void (*func)(const char*));
void jack_set_info_function(void (*func)(const char*));
void jack_free(void* ptr);

/* transport.h */

int  jack_transport_locate(jack_client_t* client, jack_nframes_t frame);
jack_transport_state_t jack_transport_query(const jack_client_t* client, jack_position_t* pos);
jack_nframes_t jack_get_current_transport_frame(const jack_client_t* client);
int  jack_transport_reposition(jack_client_t* client, const jack_position_t* pos);
void jack_transport_start(jack_client_t* client);
void jack_transport_stop(jack_client_t* client);

/* statistics.h */

float jack_get_xrun_delayed_usecs(jack_client_t* client);

/* errno.h */

#define	EEXIST 17
""")

_lib = _ffi.dlopen("jack")

CALL_AGAIN = 0
"""Possible return value for process callback."""
STOP_CALLING = 1
"""Possible return value for process callback."""
SUCCESS = 0
"""Possible return value for several callbacks."""
FAILURE = 1
"""Possible return value for several callbacks."""


class Client(object):

    """A client that can connect to the JACK audio server."""

    class Ports(object):

        """A list of input/output ports.

        This class is not meant to be instantiated directly.  It is only
        used as :attr:`Client.inports` and :attr:`Client.outports`.

        The ports can be accessed by indexing or by iteration.

        New ports can be added with :meth:`register`, existing ports can
        be removed by calling their :meth:`OwnPort.unregister` method.

        """

        def __init__(self, client, flag):
            self._client = client
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

        def register(self, shortname, is_terminal=False):
            """Create a new input/output port.

            The new :class:`OwnPort` object is automatically added to
            :attr:`Client.inports`/:attr:`Client.outports`.

            Parameters
            ----------
            shortname : str
                Each port has a short name.  The port's full name contains
                the name of the client concatenated with a colon (:)
                followed by its short name.  The :func:`port_name_size` is
                the maximum length of this full name.  Exceeding that will
                cause the port registration to fail.

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

            Returns
            -------
            OwnPort
                A new :class:`OwnPort` instance.

            """
            port = self._client._register_port(shortname, is_terminal,
                                               self._flag)
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

    def __init__(self, name, use_exact_name=False, no_start_server=False,
                 servername=None, session_id=None):
        """Create a new JACK client.

        Parameters
        ----------
        name : str
            The desired client name of at most :func:`client_name_size`
            characters.  The name scope is local to each server.
            Unless forbidden by the `use_exact_name` option, the server
            will modify this name to create a unique variant, if needed.

        Other Parameters
        ----------------
        use_exact_name : bool
            Whether an error should be raised if `name` is not unique.
        no_start_server : bool
            Do not automatically start the JACK server when it is not
            already running.  This option is always selected if
            ``JACK_NO_START_SERVER`` is defined in the calling process
            environment.
        servername : str
            Selects from among several possible concurrent server
            instances.
            Server names are unique to each user.  If unspecified, use
            ``"default"`` unless ``JACK_DEFAULT_SERVER`` is defined in
            the process environment.
        session_id : str
            Pass a SessionID Token. This allows the sessionmanager to
            identify the client again.

        """
        status = _ffi.new("jack_status_t*")
        args = [name.encode(), _lib.JackNullOption, status]
        if use_exact_name:
            args[1] |= _lib.JackUseExactName
        if no_start_server:
            args[1] |= _lib.JackNoStartServer
        if servername:
            args[1] |= _lib.JackServerName
            args.append(_ffi.new("char[]", servername.encode()))
        if session_id:
            args[1] |= _lib.JackSessionID
            args.append(_ffi.new("char[]", session_id.encode()))
        self._ptr = _lib.jack_client_open(*args)
        if not self._ptr:
            status = status[0]
            raise JackError(
                "{0} ({1})".format(decode_status(status), hex(status)))

        self._inports = self.Ports(self, _lib.JackPortIsInput)
        self._outports = self.Ports(self, _lib.JackPortIsOutput)
        self._keepalive = []

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
        return _ffi.string(_lib.jack_get_client_name(self._ptr)).decode()

    @property
    def samplerate(self):
        """The sample rate of the JACK system (read-only)."""
        return _lib.jack_get_sample_rate(self._ptr)

    @property
    def blocksize(self):
        """The JACK block size (must be a power of two).

        The current maximum size that will ever be passed to the process
        callback.  It should only be queried *before* :meth:`activate`
        has been called.  This size may change, clients that depend on
        it must register a callback with :meth:`set_blocksize_callback`
        so they will be notified if it does.

        Changing the blocksize stops the JACK engine process cycle, then
        calls all registered callback functions (see
        :meth:`set_blocksize_callback`) before restarting the process
        cycle.  This will cause a gap in the audio flow, so it should
        only be done at appropriate stopping points.

        """
        return _lib.jack_get_buffer_size(self._ptr)

    @blocksize.setter
    def blocksize(self, blocksize):
        _check(_lib.jack_set_buffer_size(self._ptr, blocksize),
               "Error setting JACK blocksize")

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
        :attr:`last_frame_time` to relate time in other threads to JACK
        time.

        """
        return _lib.jack_frame_time(self._ptr)

    @property
    def last_frame_time(self):
        """The precise time at the start of the current process cycle.

        This may only be used from the process callback (see
        :meth:`set_process_callback`), and can be used to interpret
        timestamps generated by :attr:`frame_time` in other threads with
        respect to the current process cycle.

        This is the only jack time function that returns exact time:
        when used during the process callback it always returns the same
        value (until the next process callback, where it will return
        that value + :attr:`blocksize`, etc).  The return value is
        guaranteed to be monotonic and linear in this fashion unless an
        xrun occurs (see :meth:`set_xrun_callback`).  If an xrun occurs,
        clients must check this value again, as time may have advanced
        in a non-linear way (e.g.  cycles may have been skipped).

        """
        return _lib.jack_last_frame_time(self._ptr)

    @property
    def xrun_delayed_usecs(self):
        """Delay in microseconds due to the most recent XRUN occurrence.

        This probably only makes sense when queried from a callback
        defined using :meth:`set_xrun_callback`.

        """
        return _lib.jack_get_xrun_delayed_usecs(self._ptr)

    @property
    def inports(self):
        """A list of input :class:`Ports`.

        New ports can be created and added to this list with the
        :meth:`~Ports.register` method.  When :meth:`OwnPort.unregister`
        is called on one of the items in this list, this port is removed
        from the list.  The :meth:`~Ports.clear` method can be used to
        unregister all input ports at once.

        See Also
        --------
        Ports, OwnPort

        """
        return self._inports

    @property
    def outports(self):
        """A list of output :class:`Ports`.

        New ports can be created and added to this list with the
        :meth:`~Ports.register` method.  When :meth:`OwnPort.unregister`
        is called on one of the items in this list, this port is removed
        from the list.  The :meth:`~Ports.clear` method can be used to
        unregister all output ports at once.

        See Also
        --------
        Ports, OwnPort

        """
        return self._outports

    def owns(self, port):
        """Check if a given port belongs to `self`.

        Parameters
        ----------
        port : str or Port
            Full port name or :class:`Port`/:class:`OwnPort` object.

        """
        port = self._get_port_ptr(port)
        return bool(_lib.jack_port_is_mine(self._ptr, port))

    def activate(self):
        """Activate JACK client.

        Tell the JACK server that the program is ready to start
        processing audio.

        """
        _check(_lib.jack_activate(self._ptr), "Error activating JACK client")

    def deactivate(self):
        """De-activate JACK client.

        Tell the JACK server to remove `self` from the process graph.
        Also, disconnect all ports belonging to it, since inactive
        clients have no port connections.

        """
        _check(_lib.jack_deactivate(self._ptr),
               "Error deactivating JACK client")

    def cpu_load(self):
        """Return the current CPU load estimated by JACK.

        This is a running average of the time it takes to execute a full
        process cycle for all clients as a percentage of the real time
        available per cycle determined by the :attr:`blocksize` and
        :attr:`samplerate`.

        """
        return _lib.jack_cpu_load(self._ptr)

    def close(self, ignore_errors=True):
        """Close the JACK client."""
        if self._ptr:
            err = _lib.jack_client_close(self._ptr)
            self._ptr = _ffi.NULL
            if not ignore_errors:
                _check(err, "Error closing JACK client")

    def connect(self, source, destination):
        """Establish a connection between two ports.

        When a connection exists, data written to the source port will
        be available to be read at the destination port.

        The port types must be identical.

        Parameters
        ----------
        source : str or Port
            One end of the connection. Must be an output port.
        destination : str or Port
            The other end of the connection. Must be an input port.

        """
        if isinstance(source, Port):
            source = source.name
        if isinstance(destination, Port):
            destination = destination.name
        err = _lib.jack_connect(self._ptr, source.encode(),
                                destination.encode())
        if err == _lib.EEXIST:
            raise JackError("Connection {0!r} -> {1!r} "
                            "already exists".format(source, destination))
        _check(err,
               "Error connecting {0!r} -> {1!r}".format(source, destination))

    def disconnect(self, source, destination):
        """Remove a connection between two ports.

        Parameters
        ----------
        source, destination : str or Port
            See :meth:`connect`.

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

    def transport_locate(self, frame):
        """Reposition the JACK transport to a new frame number.

        Parameters
        ----------
        frame : int
            Frame number.

        """
        _check(_lib.jack_transport_locate(self._ptr, frame),
               "Error locating JACK transport")

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
        :meth:`activate`.  This restriction does not apply to other
        systems (e.g. Linux kernel 2.6 or OS X).

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
               "Error setting freewheel mode")

    def set_shutdown_callback(self, callback, userdata=None):
        """Register shutdown callback.

        Register a function (and optional argument) to be called if and
        when the JACK server shuts down the client thread.
        The function must be written as if it were an asynchonrous POSIX
        signal handler --- use only async-safe functions, and remember
        that it is executed from another thread.
        A typical function might set a flag or write to a pipe so that
        the rest of the application knows that the JACK client thread
        has shut down.

        .. note:: clients do not need to call this.  It exists only to
           help more complex clients understand what is going on.  It
           should be called before :meth:`activate`.

        .. note:: application should typically signal another thread to
           correctly finish cleanup, that is by calling :meth:`close`
           (since :meth:`close` cannot be called directly in the context
           of the thread that calls the shutdown callback).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever the JACK
            daemon is shutdown.  It must have this signature::

                callback(status:int, reason:str, userdata) -> None

            The argument `status` can be decoded with
            :func:`decode_status`.

            Note that after server shutdown, `self`
            is *not* deallocated by libjack, the application is
            responsible to properly use :meth:`close` to release client
            ressources.

            .. warning:: :meth:`close` cannot be safely used inside the
               shutdown callback and has to be called outside of the
               callback context.
        userdata : anything
            This will be passed as third argument when `callback` is
            called.

        """
        @self._callback("JackInfoShutdownCallback")
        def callback_wrapper(code, reason, _):
            return callback(code, _ffi.string(reason).decode(), userdata)

        _lib.jack_on_info_shutdown(self._ptr, callback_wrapper, _ffi.NULL)

    def set_process_callback(self, callback, userdata=None):
        """Register process callback.

        Tell the Jack server to call `callback` whenever there is work
        be done, passing `userdata` as the second argument.

        The code in the supplied function must be suitable for real-time
        execution.  That means that it cannot call functions that might
        block for a long time. This includes malloc, free, printf,
        pthread_mutex_lock, sleep, wait, poll, select, pthread_join,
        pthread_cond_wait, etc, etc.

        .. note:: This function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called by the engine anytime
            there is work to be done.  It must have this signature::

                callback(frames:int, userdata) -> int

            The argument `frames` specifies the number of frames that
            have to be processed in the current audio block. It will be
            the same number as :attr:`blocksize` and it will be a power
            of two.
            The `callback` must return zero on success (if `callback`
            shall be called again for the next audio block) and non-zero
            on error (if `callback` shall not be called again).
            You can use :data:`CALL_AGAIN` and :data:`STOP_CALLING`,
            respectively.
        userdata : anything
            This will be passed as second argument whenever `callback`
            is called.

        """
        @self._callback("JackProcessCallback", error=STOP_CALLING)
        def callback_wrapper(frames, _):
            return callback(frames, userdata)

        _check(_lib.jack_set_process_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting process callback")

    def set_freewheel_callback(self, callback, userdata=None):
        """Register freewheel callback.

        Tell the JACK server to call `callback` whenever we enter or
        leave "freewheel" mode, passing `userdata` as the second
        argument. The first argument to the callback will be ``True`` if
        JACK is entering freewheel mode, and ``False`` otherwise.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever jackd starts
            or stops freewheeling.  It must have this signature::

                callback(starting:bool, userdata) -> None

        userdata : anything
            This will be passed as second argument whenever `callback`
            is called.

        See Also
        --------
        set_freewheel

        """
        @self._callback("JackFreewheelCallback")
        def callback_wrapper(starting, _):
            return callback(bool(starting), userdata)

        _check(_lib.jack_set_freewheel_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting freewheel callback")

    def set_blocksize_callback(self, callback, userdata=None):
        """Register blocksize callback.

        Tell JACK to call `callback` whenever the size of the the buffer
        that will be passed to the process callback is about to change.
        Clients that depend on knowing the buffer size must supply a
        `callback` before activating themselves.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is invoked whenever the JACK
            engine buffer size changes.  It must have this signature::

                callback(blocksize:int, userdata) -> int

            The `callback` must return zero on success and non-zero on
            error.  You can use :data:`SUCCESS` and :data:`FAILURE`,
            respectively.

            Although this function is called in the JACK process thread,
            the normal process cycle is suspended during its operation,
            causing a gap in the audio flow.  So, the `callback` can
            allocate storage, touch memory not previously referenced,
            and perform other operations that are not realtime safe.
        userdata : anything
            This will be passed as second argument whenever `callback`
            is called.

        """
        @self._callback("JackBufferSizeCallback", error=FAILURE)
        def callback_wrapper(blocksize, _):
            return callback(blocksize, userdata)

        _check(_lib.jack_set_buffer_size_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting blocksize callback")

    def set_samplerate_callback(self, callback, userdata=None):
        """Register samplerate callback.

        Tell the JACK server to call `callback` whenever the system
        sample rate changes.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called when the engine sample
            rate changes.  It must have this signature::

                callback(samplerate:int, userdata) -> int

            The argument `samplerate` is the new engine sample rate.
            The `callback` must return zero on success and non-zero on
            error.  You can use :data:`SUCCESS` and :data:`FAILURE`,
            respectively.
        userdata : anything
            This will be passed as second argument whenever `callback`
            is called.

        """
        @self._callback("JackSampleRateCallback", error=FAILURE)
        def callback_wrapper(samplerate, _):
            return callback(samplerate, userdata)

        _check(_lib.jack_set_sample_rate_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting samplerate callback")

    def set_client_registration_callback(self, callback, userdata=None):
        """Register client registration callback.

        Tell the JACK server to call `callback` whenever a client is
        registered or unregistered, passing `userdata` as a parameter.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever a client is
            registered or unregistered.  It must have this signature::

                callback(name:str, register:bool, userdata) -> None

            The first argument contains the client name, the second
            argument is ``True`` if the client is being registered and
            ``False`` if the client is being unregistered.
        userdata : anything
            This will be passed as third argument whenever `callback`
            is called.

        """
        @self._callback("JackClientRegistrationCallback")
        def callback_wrapper(name, register, _):
            return callback(_ffi.string(name).decode(), bool(register),
                            userdata)

        _check(_lib.jack_set_client_registration_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting client registration callback")

    def set_port_registration_callback(self, callback, userdata=None):
        """Register port registration callback.

        Tell the JACK server to call `callback` whenever a port is
        registered or unregistered, passing `userdata` as a parameter.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function function that is called whenever a
            port is registered or unregistered.
            It must have this signature::

                callback(port:Port, register:bool, userdata) -> None

            The first argument is a :class:`Port` object (or an
            :class:`OwnPort`), the second argument is ``True`` if the
            port is being registered, ``False`` if the port is being
            unregistered.
        userdata : anything
            This will be passed as third argument whenever `callback` is
            called.

        """
        @self._callback("JackPortRegistrationCallback")
        def callback_wrapper(port, register, _):
            port = _lib.jack_port_by_id(self._ptr, port)
            port = OwnPort(port, self) if self.owns(port) else Port(port)
            return callback(port, bool(register), userdata)

        _check(_lib.jack_set_port_registration_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting port registration callback")

    def set_port_connect_callback(self, callback, userdata=None):
        """Register port connect callback.

        Tell the JACK server to call `callback` whenever a port is
        connected or disconnected, passing `userdata` as a parameter.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever a port is
            connected or disconnected.  It must have this signature::

                callback(a:Port, b:Port, connect:bool, userdata) -> None

            The first and second arguments contain :class:`Port` (or
            :class:`OwnPort`) objects of the ports which are connected
            or disconnected.  The third argument is ``True`` if the
            ports were connected and ``False`` if the ports were
            disconnected.
        userdata : anything
            This will be passed as fourth argument whenever `callback`
            is called.

        """
        @self._callback("JackPortConnectCallback")
        def callback_wrapper(a, b, connect, _):
            a = _lib.jack_port_by_id(self._ptr, a)
            a = OwnPort(a, self) if self.owns(a) else Port(a)
            b = _lib.jack_port_by_id(self._ptr, b)
            b = OwnPort(b, self) if self.owns(b) else Port(b)
            return callback(a, b, bool(connect), userdata)

        _check(_lib.jack_set_port_connect_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting port connect callback")

    def set_port_rename_callback(self, callback, userdata=None):
        """Register port rename callback.

        Tell the JACK server to call `callback` whenever a port is
        renamed, passing `userdata` as a parameter.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever the port name
            has been changed.  It must have this signature::

                callback(port:Port, old:str, new:str, userdata) -> int

            The first argument is the port that has been renamed (a
            :class:`Port` or :class:`OwnPort` object); the second and
            third argument is the old and new name, respectively.
            The `callback` must return zero on success and non-zero on
            error.  You can use :data:`SUCCESS` and :data:`FAILURE`,
            respectively.
        userdata : anything
            This will be passed as fourth argument whenever `callback`
            is called.

        """
        @self._callback("JackPortRenameCallback", error=FAILURE)
        def callback_wrapper(port, old_name, new_name, _):
            port = _lib.jack_port_by_id(self._ptr, port)
            port = OwnPort(port, self) if self.owns(port) else Port(port)
            return callback(port, _ffi.string(old_name).decode(),
                            _ffi.string(new_name).decode(), userdata)

        _check(_lib.jack_set_port_rename_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting port rename callback")

    def set_graph_order_callback(self, callback, userdata=None):
        """Register graph order callback.

        Tell the JACK server to call `callback` whenever the processing
        graph is reordered, passing `userdata` as a parameter.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever the
            processing graph is reordered.
            It must have this signature::

                callback(userdata) -> int

            The `callback` must return zero on success and non-zero on
            error.  You can use :data:`SUCCESS` and :data:`FAILURE`,
            respectively.
        userdata : anything
            This will be passed as argument whenever `callback` is
            called.

        """
        @self._callback("JackGraphOrderCallback", error=FAILURE)
        def callback_wrapper(_):
            return callback(userdata)

        _check(_lib.jack_set_graph_order_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting graph order callback")

    def set_xrun_callback(self, callback, userdata=None):
        """Register xrun callback.

        Tell the JACK server to call `callback` whenever there is an
        xrun, passing `userdata` as a parameter.

        All "notification events" are received in a separated non RT
        thread, the code in the supplied function does not need to be
        suitable for real-time execution.

        .. note:: this function cannot be called while the client is
           activated (after :meth:`activate` has been called).

        Parameters
        ----------
        callback : callable
            User-supplied function that is called whenever an xrun has
            occured.  It must have this signature::

                callback(userdata) -> int

            The `callback` must return zero on success and non-zero on
            error.  You can use :data:`SUCCESS` and :data:`FAILURE`,
            respectively.
        userdata : anything
            This will be passed as argument whenever `callback` is
            called.

        See Also
        --------
        :attr:`xrun_delayed_usecs`

        """
        @self._callback("JackXRunCallback", error=FAILURE)
        def callback_wrapper(_):
            return callback(userdata)

        _check(_lib.jack_set_xrun_callback(
            self._ptr, callback_wrapper, _ffi.NULL),
            "Error setting xrun callback")

    def get_uuid_for_client_name(self, name):
        """Get the session ID for a client name.

        The session manager needs this to reassociate a client name to
        the session ID.

        """
        uuid = _ffi.gc(_lib.jack_get_uuid_for_client_name(
            self._ptr, name.encode()), _lib.jack_free)
        if not uuid:
            raise JackError("Unable to get session ID for {0!r}".format(name))
        return _ffi.string(uuid).decode()

    def get_client_name_by_uuid(self, uuid):
        """Get the client name for a session ID.

        In order to snapshot the graph connections, the session manager
        needs to map session IDs to client names.

        """
        name = _ffi.gc(_lib.jack_get_client_name_by_uuid(
            self._ptr, uuid.encode()), _lib.jack_free)
        if not name:
            raise JackError("Unable to get client name for {0!r}".format(uuid))
        return _ffi.string(name).decode()

    def get_port_by_name(self, name):
        """Get port by name.

        Given a full port name, this returns a :class:`Port` or an
        :class:`OwnPort` object.

        """
        port_ptr = _lib.jack_port_by_name(self._ptr, name.encode())
        if not port_ptr:
            raise JackError("Port {0!r} not available".format(name))
        if self.owns(port_ptr):
            return OwnPort(port_ptr, self)
        return Port(port_ptr)

    def get_all_connections(self, port):
        """Return a list of ports which the given port is connected to.

        This differs from :attr:`OwnPort.connections` in two important
        respects:

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

    def get_ports(self, name_pattern="", type_pattern="",
                  is_input=False, is_output=False, is_physical=False,
                  can_monitor=False, is_terminal=False):
        """Return a list of selected ports.

        Parameters
        ----------
        name_pattern : str
            A regular expression used to select ports by name.  If
            empty, no selection based on name will be carried out.
        type_pattern : str
            A regular expression used to select ports by type.  If
            empty, no selection based on type will be carried out.
        is_input, is_output, is_physical, can_monitor, is_terminal : bool
            Select ports by their flags.  If none of them are ``True``,
            no selection based on flags will be carried out.

        Returns
        -------
        list of Port/OwnPort
            All ports that satisfy the given conditions.

        """
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
            self._ptr, name_pattern.encode(), type_pattern.encode(), flags),
            _lib.jack_free)
        return self._port_list_from_pointers(names)

    def _callback(self, cdecl, **kwargs):
        """Wrapper for ffi.callback() that keeps callback alive."""
        def callback_decorator(python_callable):
            function_ptr = _ffi.callback(cdecl, python_callable, **kwargs)
            self._keepalive.append(function_ptr)
            return function_ptr
        return callback_decorator

    def _register_port(self, shortname, is_terminal, flags):
        """Create a new port."""
        if is_terminal:
            flags |= _lib.JackPortIsTerminal
        port_ptr = _lib.jack_port_register(self._ptr, shortname.encode(),
                                           "32 bit float mono audio".encode(),
                                           flags, 0)
        if not port_ptr:
            raise JackError(
                "{0!r}: port registration failed".format(shortname))
        return OwnPort(port_ptr, self)

    def _port_list_from_pointers(self, names):
        """Get list of Port objects from char**."""
        ports = []
        if names:
            idx = 0
            while True:
                name = names[idx]
                if not name:
                    break
                ports.append(self.get_port_by_name(_ffi.string(name).decode()))
                idx += 1
        return ports

    def _get_port_ptr(self, port):
        """Get port pointer from Port object or string or port pointer."""
        if isinstance(port, Port):
            port = port._ptr
        elif isinstance(port, str):
            port = self.get_port_by_name(port)._ptr
        elif not isinstance(port, _ffi.CData):
            raise TypeError("{0!r} is not a JACK port".format(port))
        return port


class Port(object):

    """A JACK port.

    This class cannot be instantiated directly.  Instead, instances of
    this class are returned from :meth:`Client.get_port_by_name`,
    :meth:`Client.get_ports`, :meth:`Client.get_all_connections` and
    :attr:`OwnPort.connections`.
    In addition, instances of this class are available in the callbacks
    which are set with :meth:`Client.set_port_registration_callback`,
    :meth:`Client.set_port_connect_callback` or
    :meth:`Client.set_port_rename_callback`.

    Note, however, that if the used :class:`Client` owns the respective
    port, instances of :class:`OwnPort` (instead of :class:`Port`) will
    be created.

    """

    def __init__(self, port_ptr):
        if not isinstance(port_ptr, _ffi.CData) or \
                _ffi.typeof(port_ptr) != _ffi.typeof("jack_port_t*"):
            raise TypeError("Invalid port pointer")
        self._ptr = port_ptr

    def __repr__(self):
        return "jack.{0.__class__.__name__}({0.name!r})".format(self)

    @property
    def name(self):
        """Full name of the JACK port (read-only)."""
        return _ffi.string(_lib.jack_port_name(self._ptr)).decode()

    @property
    def shortname(self):
        """Short name of the JACK port, not including "client_name:".

        Must be unique among all ports owned by a client.

        May be modified at any time.  If the resulting full name
        (including the "client_name:" prefix) is longer than
        :func:`port_name_size`, it will be truncated.

        """
        return _ffi.string(_lib.jack_port_short_name(self._ptr)).decode()

    @shortname.setter
    def shortname(self, shortname):
        _check(_lib.jack_port_set_name(self._ptr, shortname.encode()),
               "Error setting port name")

    @property
    def uuid(self):
        """The UUID of the JACK port."""
        return _lib.jack_port_uuid(self._ptr)

    @property
    def is_input(self):
        """Can the port receive data?"""
        return bool(self._portflags() & _lib.JackPortIsInput)

    @property
    def is_output(self):
        """Can data be read from this port?"""
        return bool(self._portflags() & _lib.JackPortIsOutput)

    @property
    def is_physical(self):
        """Does it correspond to some kind of physical I/O connector?"""
        return bool(self._portflags() & _lib.JackPortIsPhysical)

    @property
    def can_monitor(self):
        """Does a call to :meth:`request_monitor` make sense?"""
        return bool(self._portflags() & _lib.JackPortCanMonitor)

    @property
    def is_terminal(self):
        """Is the data consumed/generated?"""
        return bool(self._portflags() & _lib.JackPortIsTerminal)

    @property
    def type(self):
        """Port type."""
        return _ffi.string(_lib.jack_port_type(self._ptr)).decode()

    @property
    def type_id(self):
        """Port type ID."""
        return _lib.jack_port_type_id(self._ptr)

    def request_monitor(self, onoff):
        """Set input monitoring.

        If :attr:`can_monitor` is ``True``, turn input monitoring on or
        off.  Otherwise, do nothing.

        Parameters
        ----------
        onoff : bool
            If ``True``, switch monitoring on; if ``False``, switch it
            off.

        """
        _check(_lib.jack_port_request_monitor(self._ptr, onoff),
               "Unable to switch monitoring on/off")

    def _portflags(self):
        return _lib.jack_port_flags(self._ptr)


class OwnPort(Port):

    """A JACK port owned by a Client object.

    This class is derived from :class:`Port`.  Therfore,
    :class:`OwnPort` objects can do everything that :class:`Port`
    objects can, plus some more things.

    This class cannot be instantiated directly.  Instead, instances of
    this class are returned from :meth:`Client.get_port_by_name`,
    :meth:`Client.get_ports`, :meth:`Client.get_all_connections` and
    :attr:`connections`.
    In addition, instances of this class are available in the callbacks
    which are set with :meth:`Client.set_port_registration_callback`,
    :meth:`Client.set_port_connect_callback` or
    :meth:`Client.set_port_rename_callback`.

    Note, however, that if the used :class:`Client` doesn't own the
    respective port, instances of :class:`Port` (instead of
    :class:`OwnPort`) will be created.

    New JACK ports can be created with the
    :meth:`~Client.Ports.register` method of :attr:`Client.inports` and
    :attr:`Client.outports`.

    """

    def __init__(self, port_ptr, client):
        Port.__init__(self, port_ptr)
        self._client = client

    def __eq__(self, other):
        """This is needed for list.remove() in unregister()."""
        return (self._ptr == other._ptr and
                self._client._ptr == other._client._ptr)

    def __ne__(self, other):
        """This should be implemented whenever __eq__() is implemented."""
        return not self.__eq__(other)

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
        """Am I *directly* connected to `port`?

        Parameters
        ----------
        port : str or Port
            Full port name or :class:`Port`/:class:`OwnPort` object.

        """
        if isinstance(port, Port):
            port = port.name
        return bool(_lib.jack_port_connected_to(self._ptr, port.encode()))

    def connect(self, port):
        """Connect to given port:

        Parameters
        ----------
        port : str or Port
            Full port name or :class:`Port`/:class:`OwnPort` object.

        See Also
        --------
        Client.connect

        """
        if not isinstance(port, Port):
            port = self._client.get_port_by_name(port)
        if self.is_output:
            source = self
            if not port.is_input:
                raise ValueError("Input port expected")
            destination = port
        elif self.is_input:
            destination = self
            if not port.is_output:
                raise ValueError("Output port expected")
            source = port
        else:
            assert False
        self._client.connect(source.name, destination.name)

    def disconnect(self):
        """Disconnect all connections of this port."""
        _check(_lib.jack_port_disconnect(self._client._ptr, self._ptr),
               "Error disconnecting {0!r}".format(self.name))

    def unregister(self):
        """Unregister port.

        Remove the port from the client, disconnecting any existing
        connections.  This also removes the port from
        :attr:`Client.inports`/:attr:`Client.outports`.

        """
        if self.is_input:
            ports = self._client.inports
        elif self.is_output:
            ports = self._client.outports
        else:
            assert False
        ports._portlist.remove(self)
        name = self.name  # store name for error message
        err = _lib.jack_port_unregister(self._client._ptr, self._ptr)
        self._ptr = _ffi.NULL
        _check(err, "Error unregistering {0!r}".format(name))

    def get_buffer(self):
        """Get buffer for audio data.

        This returns a buffer holding the memory area associated with
        the specified port.  For an output port, it will be a memory
        area that can be written to; for an input port, it will be an
        area containing the data from the port's connection(s), or
        zero-filled.  If there are multiple inbound connections, the
        data will be mixed appropriately.

        Caching output ports is DEPRECATED in Jack 2.0, due to some new
        optimization (like "pipelining").  Port buffers have to be
        retrieved in each callback for proper functioning.

        """
        blocksize = self._client.blocksize
        return _ffi.buffer(_ffi.cast("float*", _lib.jack_port_get_buffer(
            self._ptr, blocksize)), blocksize * _ffi.sizeof("float"))

    def get_array(self):
        """Get audio buffer as NumPy array.

        See Also
        --------
        get_buffer

        """
        import numpy as np
        return np.frombuffer(self.get_buffer(), dtype=np.float32)


def decode_status(status):
    """Return string corresponding to ``JackStatus`` error code."""
    if status & _lib.JackInvalidOption:
        msg = "The operation contained an invalid or unsupported option"
    elif status & _lib.JackShmFailure:
        msg = "Unable to access shared memory"
    elif status & _lib.JackVersionError:
        msg = "Client's protocol version does not match"
    elif status & _lib.JackClientZombie:
        msg = "Zombie!"
    elif status & _lib.JackNoSuchClient:
        msg = "Requested client does not exist"
    elif status & _lib.JackLoadFailure:
        msg = "Unable to load internal client"
    elif status & _lib.JackInitFailure:
        msg = "Unable to initialize client"
    elif status & _lib.JackBackendError:
        msg = "Backend error"
    elif status & _lib.JackNameNotUnique & _lib.JackFailure:
        msg = "The client name is not unique"
    elif status & _lib.JackServerFailed:
        msg = "Unable to connect to the JACK server"
    elif status & _lib.JackServerError:
        msg = "Communication error with the JACK server"
    elif status & _lib.JackFailure:
        msg = "Overall operation failed"
    else:
        msg = "Unknown error"
    return msg


class JackError(Exception):

    """Exception for all kinds of JACK-related errors."""

    pass


def version():
    """Get tuple of major/minor/micro/protocol version."""
    major_ptr = _ffi.new("int*")
    minor_ptr = _ffi.new("int*")
    micro_ptr = _ffi.new("int*")
    proto_ptr = _ffi.new("int*")
    _lib.jack_get_version(major_ptr, minor_ptr, micro_ptr, proto_ptr)
    return major_ptr[0], minor_ptr[0], micro_ptr[0], proto_ptr[0]


def version_string():
    """Get human-readable JACK version."""
    return _ffi.string(_lib.jack_get_version_string()).decode()


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

    """
    _set_some_function(callback, _lib.jack_set_error_function)


def set_info_function(callback=None):
    """Set the callback for info message display.

    Set it to ``None`` to restore default info callback function
    (which prints the info message plus a newline to stderr).

    """
    _set_some_function(callback, _lib.jack_set_info_function)


def client_pid(name):
    """Return PID of a JACK client.

    Parameters
    ----------
    name : str
        Name of the JACK client whose PID shall be returned.

    Returns
    -------
    int
        PID of `name`.  If not available, 0 will be returned.

    """
    return _lib.jack_get_client_pid(name.encode())


def _set_some_function(callback, setter):
    """Helper for set_error_function() and set_info_function()."""
    if callback is None:
        callback_wrapper = _ffi.NULL
    else:
        @_ffi.callback("void (*)(const char*)")
        def callback_wrapper(msg):
            return callback(_ffi.string(msg).decode())

        _keepalive[setter] = callback_wrapper
    setter(callback_wrapper)

_keepalive = {}


def _check(error_code, msg):
    """Check error code and raise JackError if non-zero."""
    if error_code:
        raise JackError("{0} ({1})".format(msg, error_code))
