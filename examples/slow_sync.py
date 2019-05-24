#!/usr/bin/env python3
"""Show how slow-sync clients work."""
import time

import jack

slow = jack.Client('Slow')

slow.pos = 0
slow.ready_at = None
slow.seek_time = 0.1


@slow.set_sync_callback
def slow_sync_callback(state, pos):
    now = time.time()
    print(jack.TransportState(state), pos.frame, end=' ')
    if state == jack.STOPPED:
        if slow.pos == pos.frame:
            print('ready')
            return True
        if slow.ready_at is None:
            slow.ready_at = now + slow.seek_time
        if slow.ready_at < now:
            print('just got ready')
            slow.pos = pos.frame
            slow.ready_at = None
            return True
        print('will be ready in {:.2f} seconds'.format(slow.ready_at - now))
    elif state == jack.STARTING:
        if slow.pos == pos.frame:
            print('ready')
            return True
        if slow.ready_at is None:
            slow.ready_at = now + slow.seek_time
        if slow.ready_at < now:
            print('just got ready')
            slow.pos = pos.frame
            slow.ready_at = None
            return True
        print('will be ready in {:.2f} seconds'.format(slow.ready_at - now))
        return False
    elif state == jack.ROLLING:
        assert slow.pos != pos.frame
        assert slow.ready_at is not None
        if slow.ready_at < now:
            print('just caught up')
            slow.pos = pos.frame
            slow.ready_at = None
            return True
        print('will catch up in {:.2f} seconds'.format(slow.ready_at - now))
        return False
    else:
        assert False
    return False


# Make sure transport is stopped and at 0 initially
slow.transport_stop()
slow.transport_frame = 0

print('== setting custom sync timeout')
slow.set_sync_timeout(int(0.5 * slow.seek_time * 1000 * 1000))

with slow:
    time.sleep(0.1)  # Time to show STOPPED
    print('== starting transport')
    slow.transport_start()
    time.sleep(0.1)  # Time to show STARTING
    print('== stopping transport')
    slow.transport_stop()
    print('== seeking to 123')
    slow.transport_frame = 123
    time.sleep(0.5 * slow.seek_time)
    print('== starting transport')
    slow.transport_start()
    time.sleep(slow.seek_time)
    print('== stopping transport')
    slow.transport_stop()
    print('== setting default sync timeout')
    slow.set_sync_timeout(2 * 1000 * 1000)
    print('== seeking to 123')
    slow.transport_frame = 123
    time.sleep(0.5 * slow.seek_time)
    print('== starting transport')
    slow.transport_start()
    time.sleep(slow.seek_time)
    slow.transport_stop()
