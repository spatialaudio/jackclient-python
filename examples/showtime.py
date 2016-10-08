#!/usr/bin/env python3

"""Display information about time, transport state et cetera.

This is somewhat modeled after the "showtime.c" example of JACK.
https://github.com/jackaudio/example-clients/blob/master/showtime.c
https://github.com/jackaudio/jack2/blob/master/example-clients/showtime.c

"""
from contextlib import suppress
import time
import sys

import jack


try:
    client = jack.Client('showtime')
except jack.JackError:
    sys.exit('JACK server not running?')


def showtime():
    state, pos = client.transport_query()
    items = []
    items.append('frame = {}  frame_time = {} usecs = {} '.format(
        pos['frame'], client.frame_time, pos['usecs']))
    items.append('state: {}'.format(state))
    with suppress(KeyError):
        items.append('BBT: {bar:3}|{beat}|{tick:04}'.format(**pos))
    with suppress(KeyError):
        items.append('TC: ({frame_time:.6f}, {next_time:.6f})'.format(**pos))
    with suppress(KeyError):
     	items.append('BBT offset: ({bbt_offset})'.format(**pos))
    with suppress(KeyError):
     	items.append(
            'audio/video: ({audio_frames_per_video_frame})'.format(**pos))
    with suppress(KeyError):
        video_offset = pos['video_offset']
        if video_offset:
            items.append(' video@: ({})'.format(video_offset))
        else:
            items.append(' no video');
    print(*items, sep='\t')


@client.set_shutdown_callback
def shutdown(status, reason):
    sys.exit('JACK shut down, exiting ...')


with client:
    try:
        while True:
            time.sleep(0.00002)
            showtime()
    except KeyboardInterrupt:
        print('signal received, exiting ...', file=sys.stderr)
        sys.exit(0)
