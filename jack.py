# Copyright (c) 2014-2015 Matthias Geier
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
__version__ = "0.2.0"

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
typedef uint64_t jack_unique_t;
typedef uint64_t jack_time_t;
typedef uint32_t jack_nframes_t;
typedef enum {

    JackPositionBBT = 0x10,     /**< Bar, Beat, Tick */
    JackPositionTimecode = 0x20,        /**< External timecode */
    JackBBTFrameOffset =      0x40,     /**< Frame offset of BBT information */
    JackAudioVideoRatio =     0x80, /**< audio frames per video frame */
    JackVideoFrameOffset =   0x100  /**< frame offset of first video frame */

} jack_position_bits_t;

struct _jack_position {
    jack_unique_t       unique_1;       /**< unique ID */
    jack_time_t         usecs;          /**< monotonic, free-rolling */
    jack_nframes_t      frame_rate;     /**< current frame rate (per second) */
    jack_nframes_t      frame;          /**< frame number, always present */

    jack_position_bits_t valid;         /**< which other fields are valid */

    /* JackPositionBBT fields: */
    int32_t             bar;            /**< current bar */
    int32_t             beat;           /**< current beat-within-bar */
    int32_t             tick;           /**< current tick-within-beat */
    double              bar_start_tick;

    float               beats_per_bar;  /**< time signature "numerator" */
    float               beat_type;      /**< time signature "denominator" */
    double              ticks_per_beat;
    double              beats_per_minute;

    /* JackPositionTimecode fields:     (EXPERIMENTAL: could change) */
    double              frame_time;     /**< current time in seconds */
    double              next_time;      /**< next sequential frame_time
                         (unless repositioned) */

    /* JackBBTFrameOffset fields: */
    jack_nframes_t      bbt_offset;     /**< frame offset for the BBT fields
                         (the given bar, beat, and tick
                         values actually refer to a time
                         frame_offset frames before the
                         start of the cycle), should
                         be assumed to be 0 if
                         JackBBTFrameOffset is not
                         set. If JackBBTFrameOffset is
                         set and this value is zero, the BBT
                         time refers to the first frame of this
                         cycle. If the value is positive,
                         the BBT time refers to a frame that
                         many frames before the start of the
                         cycle. */

    /* JACK video positional data (experimental) */

    float               audio_frames_per_video_frame; /**< number of audio frames
                         per video frame. Should be assumed
                         zero if JackAudioVideoRatio is not
                         set. If JackAudioVideoRatio is set
                         and the value is zero, no video
                         data exists within the JACK graph */

    jack_nframes_t      video_offset;   /**< audio frame at which the first video
                         frame in this cycle occurs. Should
                         be assumed to be 0 if JackVideoFrameOffset
                         is not set. If JackVideoFrameOffset is
                         set, but the value is zero, there is
                         no video frame within this cycle. */

    /* For binary compatibility, new fields should be allocated from
     * this padding area with new valid bits controlling access, so
     * the existing structure size and offsets are preserved. */
    int32_t             padding[7];

    /* When (unique_1 == unique_2) the contents are consistent. */
    jack_unique_t       unique_2;       /**< unique ID */

};

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
/* deprecated: jack_engine_takeover_timebase */
float jack_cpu_load(jack_client_t* client);
jack_port_t* jack_port_register(jack_client_t* client, const char* port_name, const char* port_type, unsigned long flags, unsigned long buffer_size);
int jack_port_unregister(jack_client_t* client, jack_port_t* port);
void* jack_port_get_buffer(jack_port_t* port, jack_nframes_t);
jack_uuid_t jack_port_uuid(const jack_port_t* port);
const char* jack_port_name(const jack_port_t* port);
const char* jack_port_short_name(const jack_port_t* port);
int jack_port_flags(const jack_port_t* port);
const char* jack_port_type(const jack_port_t* port);
/* not implemented: jack_port_type_id */
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

/* midiport.h */

typedef unsigned char jack_midi_data_t;
typedef struct _jack_midi_event
{
    jack_nframes_t    time;   /* Sample index at which event is valid */
    size_t            size;   /* Number of bytes of data in buffer */
    jack_midi_data_t* buffer; /* Raw MIDI data */
} jack_midi_event_t;
uint32_t jack_midi_get_event_count(void* port_buffer);
int jack_midi_event_get(jack_midi_event_t* event, void* port_buffer, uint32_t event_index);
void jack_midi_clear_buffer(void* port_buffer);
/* not implemented: jack_midi_reset_buffer */
size_t jack_midi_max_event_size(void* port_buffer);
jack_midi_data_t* jack_midi_event_reserve(void* port_buffer, jack_nframes_t time, size_t data_size);
int jack_midi_event_write(void* port_buffer, jack_nframes_t time, const jack_midi_data_t* data, size_t data_size);
uint32_t jack_midi_get_lost_event_count(void* port_buffer);

/* errno.h */

#define EEXIST 17
""")

_lib = _ffi.dlopen("jack")

_AUDIO = b"32 bit float mono audio"
_MIDI = b"8 bit raw midi"

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
            See :attr:`Status.name_not_unique`.
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
        self._status = Status(status[0])
        if not self._ptr:
            raise JackError(str(self.status))

        self._inports = Ports(self, _AUDIO, _lib.JackPortIsInput)
        self._outports = Ports(self, _AUDIO, _lib.JackPortIsOutput)
        self._midi_inports = Ports(self, _MIDI, _lib.JackPortIsInput)
        self._midi_outports = Ports(self, _MIDI, _lib.JackPortIsOutput)
        self._keepalive = []
        self._position = _ffi.new("jack_position_t*")

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
    def status(self):
        """JACK client status.  See :class:`Status`."""
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
        """A list of audio input :class:`Ports`.

        New ports can be created and added to this list with the
        :meth:`~Ports.register` method.
        When :meth:`~OwnPort.unregister` is called on one of the items
        in this list, this port is removed from the list.
        The :meth:`~Ports.clear` method can be used to unregister all
        audio input ports at once.

        See Also
        --------
        Ports, OwnPort

        """
        return self._inports

    @property
    def outports(self):
        """A list of audio output :class:`Ports`.

        New ports can be created and added to this list with the
        :meth:`~Ports.register` method.
        When :meth:`~OwnPort.unregister` is called on one of the items
        in this list, this port is removed from the list.
        The :meth:`~Ports.clear` method can be used to unregister all
        audio output ports at once.

        See Also
        --------
        Ports, OwnPort

        """
        return self._outports

    @property
    def midi_inports(self):
        """A list of MIDI input :class:`Ports`.

        New MIDI ports can be created and added to this list with the
        :meth:`~Ports.register` method.
        When :meth:`~OwnPort.unregister` is called on one of the
        items in this list, this port is removed from the list.
        The :meth:`~Ports.clear` method can be used to unregister all
        MIDI input ports at once.

        See Also
        --------
        Ports, OwnMidiPort

        """
        return self._midi_inports

    @property
    def midi_outports(self):
        """A list of MIDI output :class:`Ports`.

        New MIDI ports can be created and added to this list with the
        :meth:`~Ports.register` method.
        When :meth:`~OwnPort.unregister` is called on one of the
        items in this list, this port is removed from the list.
        The :meth:`~Ports.clear` method can be used to unregister all
        MIDI output ports at once.

        See Also
        --------
        Ports, OwnMidiPort

        """
        return self._midi_outports

    def owns(self, port):
        """Check if a given port belongs to `self`.

        Parameters
        ----------
        port : str or Port
            Full port name or :class:`Port`, :class:`MidiPort`,
            :class:`OwnPort` or :class:`OwnMidiPort` object.

        """
        port = self._get_port_ptr(port)
        return bool(_lib.jack_port_is_mine(self._ptr, port))

    def activate(self):
        """Activate JACK client.

        Tell the JACK server that the program is ready to start
        processing audio.

        """
        _check(_lib.jack_activate(self._ptr), "Error activating JACK client")

    def deactivate(self, ignore_errors=True):
        """De-activate JACK client.

        Tell the JACK server to remove `self` from the process graph.
        Also, disconnect all ports belonging to it, since inactive
        clients have no port connections.

        """
        err = _lib.jack_deactivate(self._ptr)
        if not ignore_errors:
            _check(err, "Error deactivating JACK client")

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

        Audio ports can obviously not be connected with MIDI ports.

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

    def transport_query(self):
        """return current transport state and position.

        Return a tuple with current transport state and position informations

        Transport state
        ---------------
        Transport state can take following value :
            * 0 : Stopped
            * 1 : Rolling (playing)
            * 2 : Looping
            * 3 : Starting (preparing playback)
            * 4 : Net Starting

        Position informations
        ---------------------
        Position information are stored in CFFI object. This object have
        following attribute :
            * usecs : monotonic, free-rolling
            * frame_rate : current frame rate (per second)
            * frame : frame number (frame count since transport start)
            * valid : indicate which fields are present and valid (see below)
            * bar: current bar
            * beat: current beat-within-bar
            * tick: current tick-within-beat
            * bar_start_tick
            * bbt_offset : frame offset for the BBT fields (see below)
            * beats_per_bar : time signature "numerator"
            * beat_type : time signature "denominator"
            * ticks_per_beat : ticks per beat
            * beats_per_minute : current tempo (BPM)
            * frame_time : current time in seconds
            * next_time : next sequential frame_time (unless repositioned)
            * audio_frames_per_video_frame
            * video_offset

        valid field is can take following values (bit flag) :
            * 0x10 : bar, beat, tick, bar_start_tick, beats_per_bar,
                     beat_type, ticks_per_beat, beats_per_minute
            * 0x20 : frame_time, next_time
            * 0x40 : bbt_offset
            * 0x80 : audio_frames_per_video_frame
            * 0x100 : video_offset

        """
        transport_state = _lib.jack_transport_query(self._ptr, self._position)
        return transport_state, self._position

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
        signal handler -- use only async-safe functions, and remember
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

                callback(status:Status, reason:str, userdata) -> None

            The argument `status` is of type :class:`jack.Status`.

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
            return callback(Status(code), _ffi.string(reason).decode(),
                            userdata)

        _lib.jack_on_info_shutdown(self._ptr, callback_wrapper, _ffi.NULL)

    def set_process_callback(self, callback, userdata=None):
        """Register process callback.

        Tell the JACK server to call `callback` whenever there is work
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
            You can use the module constants :data:`CALL_AGAIN` and
            :data:`STOP_CALLING`, respectively.
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
            error. You can use the module constants :data:`jack.SUCCESS`
            and :data:`jack.FAILURE`, respectively.

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
            error. You can use the module constants :data:`jack.SUCCESS`
            and :data:`jack.FAILURE`, respectively.
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

            The first argument is a :class:`Port`, :class:`MidiPort`,
            :class:`OwnPort` or :class:`OwnMidiPort` object, the second
            argument is ``True`` if the port is being registered,
            ``False`` if the port is being unregistered.
        userdata : anything
            This will be passed as third argument whenever `callback` is
            called.

        """
        @self._callback("JackPortRegistrationCallback")
        def callback_wrapper(port, register, _):
            port = self._wrap_port_ptr(_lib.jack_port_by_id(self._ptr, port))
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

            The first and second arguments contain :class:`Port`,
            :class:`MidiPort`, :class:`OwnPort` or :class:`OwnMidiPort`
            objects of the ports which are connected or disconnected.
            The third argument is ``True`` if the ports were connected
            and ``False`` if the ports were disconnected.
        userdata : anything
            This will be passed as fourth argument whenever `callback`
            is called.

        """
        @self._callback("JackPortConnectCallback")
        def callback_wrapper(a, b, connect, _):
            a = self._wrap_port_ptr(_lib.jack_port_by_id(self._ptr, a))
            b = self._wrap_port_ptr(_lib.jack_port_by_id(self._ptr, b))
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
            :class:`Port`, :class:`MidiPort`, :class:`OwnPort` or
            :class:`OwnMidiPort` object); the second and third argument
            is the old and new name, respectively.
            The `callback` must return zero on success and non-zero on
            error. You can use the module constants :data:`jack.SUCCESS`
            and :data:`jack.FAILURE`, respectively.
        userdata : anything
            This will be passed as fourth argument whenever `callback`
            is called.

        """
        @self._callback("JackPortRenameCallback", error=FAILURE)
        def callback_wrapper(port, old_name, new_name, _):
            port = self._wrap_port_ptr(_lib.jack_port_by_id(self._ptr, port))
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
            error. You can use the module constants :data:`jack.SUCCESS`
            and :data:`jack.FAILURE`, respectively.
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
            error. You can use the module constants :data:`jack.SUCCESS`
            and :data:`jack.FAILURE`, respectively.
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

        Given a full port name, this returns a :class:`Port`,
        :class:`MidiPort`, :class:`OwnPort` or :class:`OwnMidiPort`
        object.

        """
        port_ptr = _lib.jack_port_by_name(self._ptr, name.encode())
        if not port_ptr:
            raise JackError("Port {0!r} not available".format(name))
        return self._wrap_port_ptr(port_ptr)

    def get_all_connections(self, port):
        """Return a list of ports which the given port is connected to.

        This differs from :attr:`OwnPort.connections` (also available on
        :class:`OwnMidiPort`) in two important respects:

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

    def get_ports(self, name_pattern="", is_audio=False, is_midi=False,
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
            type_pattern = b""
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

    def _callback(self, cdecl, **kwargs):
        """Wrapper for ffi.callback() that keeps callback alive."""
        def callback_decorator(python_callable):
            function_ptr = _ffi.callback(cdecl, python_callable, **kwargs)
            self._keepalive.append(function_ptr)
            return function_ptr
        return callback_decorator

    def _register_port(self, name, porttype, is_terminal, is_physical, flags):
        """Create a new port."""
        if is_terminal:
            flags |= _lib.JackPortIsTerminal
        if is_physical:
            flags |= _lib.JackPortIsPhysical
        port_ptr = _lib.jack_port_register(self._ptr, name.encode(), porttype,
                                           flags, 0)
        if not port_ptr:
            raise JackError(
                "{0!r}: port registration failed".format(name))
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
                ports.append(self.get_port_by_name(_ffi.string(name).decode()))
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
            port = OwnPort(ptr, self) if self.owns(ptr) else Port(ptr)
        elif porttype == _MIDI:
            port = OwnMidiPort(ptr, self) if self.owns(ptr) else MidiPort(ptr)
        else:
            assert False
        return port


class Port(object):

    """A JACK audio port.

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
    be created.  In case of MIDI ports, instances of :class:`MidiPort`
    or :class:`OwnMidiPort` are created.

    Besides being the type of non-owned JACK audio ports, this class
    also serves as base class for all other port classes
    (:class:`OwnPort`, :class:`MidiPort` and :class:`OwnMidiPort`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of :attr:`Client.inports`,
    :attr:`Client.outports`, :attr:`Client.midi_inports` and
    :attr:`Client.midi_outports`.

    """

    def __init__(self, port_ptr):
        self._ptr = port_ptr

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

    is_audio = property(lambda self: True, doc="This is always ``True``.")
    is_midi = property(lambda self: False, doc="This is always ``False``.")

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
        """Does a call to :meth:`request_monitor` make sense?"""
        return self._hasflag(_lib.JackPortCanMonitor)

    @property
    def is_terminal(self):
        """Is the data consumed/generated?"""
        return self._hasflag(_lib.JackPortIsTerminal)

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

    def _hasflag(self, flag):
        """Helper method for is_*()."""
        return bool(_lib.jack_port_flags(self._ptr) & flag)


class MidiPort(Port):

    """A JACK MIDI port.

    This class is derived from :class:`Port` and has exactly the same
    attributes and methods.

    This class cannot be instantiated directly (see :class:`Port`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of :attr:`Client.inports`,
    :attr:`Client.outports`, :attr:`Client.midi_inports` and
    :attr:`Client.midi_outports`.

    See Also
    --------
    Port, OwnMidiPort

    """

    is_audio = property(lambda self: False, doc="This is always ``False``.")
    is_midi = property(lambda self: True, doc="This is always ``True``.")


class OwnPort(Port):

    """A JACK audio port owned by a :class:`Client` object.

    This class is derived from :class:`Port`.  :class:`OwnPort` objects
    can do everything that :class:`Port` objects can, plus a lot more.

    This class cannot be instantiated directly (see :class:`Port`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of :attr:`Client.inports`,
    :attr:`Client.outports`, :attr:`Client.midi_inports` and
    :attr:`Client.midi_outports`.

    """

    def __init__(self, port_ptr, client):
        Port.__init__(self, port_ptr)
        self._client = client

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
            Full port name or port object.

        """
        if isinstance(port, Port):
            port = port.name
        return bool(_lib.jack_port_connected_to(self._ptr, port.encode()))

    def connect(self, port):
        """Connect to given port:

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
                   "Error disconnecting {0!r}".format(self.name))
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
        :attr:`Client.inports`, :attr:`Client.outports`,
        :attr:`Client.midi_inports` or :attr:`Client.midi_outports`.

        """
        if self.is_audio:
            listname = ""
        elif self.is_midi:
            listname = "midi_"
        if self.is_input:
            listname += "inports"
        elif self.is_output:
            listname += "outports"
        ports = getattr(self._client, listname)
        ports._portlist.remove(self)
        _check(_lib.jack_port_unregister(self._client._ptr, self._ptr),
               "Error unregistering {0!r}".format(self.name))

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

        """
        blocksize = self._client.blocksize
        return _ffi.buffer(_lib.jack_port_get_buffer(self._ptr, blocksize),
                           blocksize * _ffi.sizeof("float"))

    def get_array(self):
        """Get audio buffer as NumPy array.

        Make sure to ``import numpy`` before calling this, otherwise the
        first call might take a long time.

        See Also
        --------
        get_buffer

        """
        import numpy as np
        return np.frombuffer(self.get_buffer(), dtype=np.float32)


class OwnMidiPort(MidiPort, OwnPort):

    """A JACK MIDI port owned by a :class:`Client` object.

    This class is derived from :class:`OwnPort` and :class:`MidiPort`,
    which are themselves derived from :class:`Port`.  It has the same
    attributes and methods as :class:`OwnPort`, but :meth:`get_buffer`
    and :meth:`get_array` are disabled.  Instead, it has methods for
    sending and receiving MIDI events (to be used from within the
    process callback -- see :meth:`Client.set_process_callback`).

    This class cannot be instantiated directly (see :class:`Port`).

    New JACK audio/MIDI ports can be created with the
    :meth:`~Ports.register` method of :attr:`Client.inports`,
    :attr:`Client.outports`, :attr:`Client.midi_inports` and
    :attr:`Client.midi_outports`.

    """

    def __init__(self, *args, **kwargs):
        OwnPort.__init__(self, *args, **kwargs)
        self._event = _ffi.new("jack_midi_event_t*")

    def get_buffer(self):
        """Not available for MIDI ports."""
        raise NotImplementedError("get_buffer() not available on MIDI ports")

    def get_array(self):
        """Not available for MIDI ports."""
        raise NotImplementedError("get_array() not available on MIDI ports")

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

        """
        event = self._event
        buf = _lib.jack_port_get_buffer(self._ptr, self._client.blocksize)
        for i in range(_lib.jack_midi_get_event_count(buf)):
            err = _lib.jack_midi_event_get(event, buf, i)
            # TODO: proper error handling if this ever happens:
            assert not err, err
            yield event.time, _ffi.buffer(event.buffer, event.size)

    def clear_buffer(self):
        """Clear an event buffer.

        This should be called at the beginning of each process cycle
        before calling :meth:`reserve_midi_event` or
        :meth:`write_midi_event`.
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
            time, event, len(event)), "Error writing MIDI event")

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
    used as :attr:`Client.inports`, :attr:`Client.outports`,
    :attr:`Client.midi_inports` and :attr:`Client.midi_outports`.

    The ports can be accessed by indexing or by iteration.

    New ports can be added with :meth:`register`, existing ports can
    be removed by calling their :meth:`~OwnPort.unregister` method.

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

        The new :class:`OwnPort` or :class:`OwnMidiPort` object is
        automatically added to :attr:`Client.inports`,
        :attr:`Client.outports`, :attr:`Client.midi_inports` or
        :attr:`Client.midi_outports`.

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
        is_physical : bool
            If ``True`` the port corresponds to some kind of physical
            I/O connector.

        Returns
        -------
        Port
            A new :class:`OwnPort` or :class:`OwnMidiPort` instance.

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


class Status(object):

    """Representation of the JACK status bits."""

    def __init__(self, statuscode):
        self._code = statuscode

    def __repr__(self):
        flags = ", ".join(name for name in dir(self)
                          if not name.startswith('_') and getattr(self, name))
        if not flags:
            flags = "no flags set"
        return "<jack.Status 0x{0:x}: {1}>".format(self._code, flags)

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

        With the `use_exact_name` option of :class:`Client`, this
        situation is fatal.
        Otherwise, the name is modified by appending a dash and a
        two-digit number in the range "-01" to "-99".
        :attr:`Client.name` will return the exact string that was used.
        If the specified `name` plus these extra characters would be too
        long, the open fails instead.

        """
        return self._hasflag(_lib.JackNameNotUnique)

    @property
    def server_started(self):
        """The JACK server was started for this :class:`Client`.

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
    The `callback` function must have this signature::

        callback(message:str) -> None

    """
    _set_error_or_info_function(callback, _lib.jack_set_error_function)


def set_info_function(callback=None):
    """Set the callback for info message display.

    Set it to ``None`` to restore default info callback function
    (which prints the info message plus a newline to stderr).
    The `callback` function must have this signature::

        callback(message:str) -> None

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
        PID of `name`.  If not available, 0 will be returned.

    """
    return _lib.jack_get_client_pid(name.encode())


def _set_error_or_info_function(callback, setter):
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
