from cffi import FFI

ffibuilder = FFI()
ffibuilder.set_source('_jack', None)
ffibuilder.cdef("""

/* types.h */

typedef uint64_t jack_uuid_t;
typedef uint32_t jack_nframes_t;
typedef uint64_t jack_time_t;
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
/* not implemented: JackShutdownCallback (only JackInfoShutdownCallback is used) */
typedef void (*JackInfoShutdownCallback)(jack_status_t code, const char* reason, void* arg);
/* JACK_DEFAULT_AUDIO_TYPE: see _AUDIO */
/* JACK_DEFAULT_MIDI_TYPE: see _MIDI */
/* not implemented: jack_default_audio_sample_t (hard-coded as float) */
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
    JackTransportLooping = 2,  /* deprecated */
    JackTransportStarting = 3,
    JackTransportNetStarting = 4,
} jack_transport_state_t;
typedef uint64_t jack_unique_t;
typedef enum {
    JackPositionBBT = 0x10,
    JackPositionTimecode = 0x20,
    JackBBTFrameOffset = 0x40,
    JackAudioVideoRatio = 0x80,
    JackVideoFrameOffset = 0x100,
} jack_position_bits_t;
/* _jack_position: see below in "packed" section */
typedef struct _jack_position jack_position_t;
typedef void (*JackTimebaseCallback)(jack_transport_state_t state, jack_nframes_t nframes, jack_position_t *pos, int new_pos, void *arg);
typedef int (*JackSyncCallback)(jack_transport_state_t state, jack_position_t *pos, void *arg);
/* deprecated: jack_transport_bits_t */
/* deprecated: jack_transport_info_t */

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
/* deprecated: jack_thread_wait */
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
int jack_port_set_alias(jack_port_t *port, const char *alias);
int jack_port_unset_alias(jack_port_t *port, const char *alias);
int jack_port_get_aliases(const jack_port_t * port, char *const aliases[2]);
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

/* ringbuffer.h */

typedef struct {
    char* buf;
    size_t len;
} jack_ringbuffer_data_t;
typedef struct {
    char* buf;
    volatile size_t write_ptr;
    volatile size_t read_ptr;
    size_t size;
    size_t size_mask;
    int mlocked;
} jack_ringbuffer_t;
jack_ringbuffer_t* jack_ringbuffer_create(size_t sz);
void jack_ringbuffer_free(jack_ringbuffer_t* rb);
void jack_ringbuffer_get_read_vector(const jack_ringbuffer_t* rb, jack_ringbuffer_data_t* vec);
void jack_ringbuffer_get_write_vector(const jack_ringbuffer_t* rb, jack_ringbuffer_data_t* vec);
size_t jack_ringbuffer_read(jack_ringbuffer_t* rb, char* dest, size_t cnt);
size_t jack_ringbuffer_peek(jack_ringbuffer_t* rb, char* dest, size_t cnt);
void jack_ringbuffer_read_advance(jack_ringbuffer_t* rb, size_t cnt);
size_t jack_ringbuffer_read_space(const jack_ringbuffer_t* rb);
int jack_ringbuffer_mlock(jack_ringbuffer_t* rb);
void jack_ringbuffer_reset(jack_ringbuffer_t* rb);
void jack_ringbuffer_reset_size (jack_ringbuffer_t* rb, size_t sz);
/* Note: "char*" was changed to "unsigned char*" to support iterables of int */
size_t jack_ringbuffer_write(jack_ringbuffer_t* rb, const unsigned char* src, size_t cnt);
void jack_ringbuffer_write_advance(jack_ringbuffer_t* rb, size_t cnt);
size_t jack_ringbuffer_write_space(const jack_ringbuffer_t* rb);

/* transport.h */

int jack_release_timebase(jack_client_t* client);
int jack_set_sync_callback(jack_client_t* client, JackSyncCallback sync_callback, void* arg);
int jack_set_sync_timeout(jack_client_t* client, jack_time_t timeout);
int jack_set_timebase_callback(jack_client_t* client, int conditional, JackTimebaseCallback timebase_callback, void* arg);
int jack_transport_locate(jack_client_t* client, jack_nframes_t frame);
jack_transport_state_t jack_transport_query(const jack_client_t* client, jack_position_t* pos);
jack_nframes_t jack_get_current_transport_frame(const jack_client_t* client);
int jack_transport_reposition(jack_client_t* client, const jack_position_t* pos);
void jack_transport_start(jack_client_t* client);
void jack_transport_stop(jack_client_t* client);
/* deprecated: jack_get_transport_info */
/* deprecated: jack_set_transport_info */

/* statistics.h */

float jack_get_xrun_delayed_usecs(jack_client_t* client);

/* midiport.h */

typedef unsigned char jack_midi_data_t;
typedef struct _jack_midi_event {
    jack_nframes_t time;
    size_t size;
    jack_midi_data_t* buffer;
} jack_midi_event_t;
uint32_t jack_midi_get_event_count(void* port_buffer);
int jack_midi_event_get(jack_midi_event_t* event, void* port_buffer, uint32_t event_index);
void jack_midi_clear_buffer(void* port_buffer);
/* not implemented: jack_midi_reset_buffer */
size_t jack_midi_max_event_size(void* port_buffer);
jack_midi_data_t* jack_midi_event_reserve(void* port_buffer, jack_nframes_t time, size_t data_size);
int jack_midi_event_write(void* port_buffer, jack_nframes_t time, const jack_midi_data_t* data, size_t data_size);
uint32_t jack_midi_get_lost_event_count(void* port_buffer);

/* session.h */

char* jack_client_get_uuid(jack_client_t* client);

/* uuid.h */

extern int jack_uuid_parse(const char* buf, jack_uuid_t*);

/* metadata.h */

typedef struct {
    const char* key;
    const char* data;
    const char* type;
} jack_property_t;
int jack_set_property(jack_client_t*, jack_uuid_t subject, const char* key, const char* value, const char* type);
int jack_get_property(jack_uuid_t subject, const char* key, char** value, char** type);
typedef struct {
    jack_uuid_t subject;
    uint32_t property_cnt;
    jack_property_t* properties;
    uint32_t property_size;
} jack_description_t;
void jack_free_description(jack_description_t* desc, int free_description_itself);
int jack_get_properties(jack_uuid_t subject, jack_description_t* desc);
int jack_get_all_properties(jack_description_t** descs);
int jack_remove_property(jack_client_t* client, jack_uuid_t subject, const char* key);
int jack_remove_properties(jack_client_t* client, jack_uuid_t subject);
int jack_remove_all_properties(jack_client_t* client);
typedef enum {
    PropertyCreated,
    PropertyChanged,
    PropertyDeleted,
} jack_property_change_t;
typedef void (*JackPropertyChangeCallback)(jack_uuid_t subject, const char* key, jack_property_change_t change, void* arg);
int jack_set_property_change_callback(jack_client_t* client, JackPropertyChangeCallback callback, void* arg);
extern const char* JACK_METADATA_CONNECTED;
extern const char* JACK_METADATA_EVENT_TYPES;
extern const char* JACK_METADATA_HARDWARE;
extern const char* JACK_METADATA_ICON_LARGE;
extern const char* JACK_METADATA_ICON_NAME;
extern const char* JACK_METADATA_ICON_SMALL;
extern const char* JACK_METADATA_ORDER;
extern const char* JACK_METADATA_PORT_GROUP;
extern const char* JACK_METADATA_PRETTY_NAME;
extern const char* JACK_METADATA_SIGNAL_TYPE;
""")

# Packed structure
ffibuilder.cdef("""
struct _jack_position {
    jack_unique_t unique_1;
    jack_time_t usecs;
    jack_nframes_t frame_rate;
    jack_nframes_t frame;
    jack_position_bits_t valid;
    int32_t bar;
    int32_t beat;
    int32_t tick;
    double bar_start_tick;
    float beats_per_bar;
    float beat_type;
    double ticks_per_beat;
    double beats_per_minute;
    double frame_time;
    double next_time;
    jack_nframes_t bbt_offset;
    float audio_frames_per_video_frame;
    jack_nframes_t video_offset;
    int32_t padding[7];
    jack_unique_t unique_2;
};
""", packed=True)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
