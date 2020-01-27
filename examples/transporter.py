#!/usr/bin/env python3
"""Query or change the JACK transport state."""
import argparse
import string

import jack


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        '-c', '--client-name',
        metavar='NAME',
        default='transporter',
        help='JACK client name (default: %(default)s)')
    ap.add_argument(
        'command',
        nargs='?',
        default='status',
        choices=['query', 'rewind', 'start', 'status', 'stop', 'toggle'],
        help='transport command')

    args = ap.parse_args(args)

    try:
        client = jack.Client(args.client_name)
    except jack.JackError as exc:
        ap.exit('Could not create JACK client: {}'.format(exc))

    state = client.transport_state
    result = 0

    if args.command == 'status':
        print('JACK transport state is {}.'.format(state))
        result = 1 if state == jack.STOPPED else 0
    elif args.command == 'query':
        print('State: {}'.format(state))
        info = client.transport_query()[1]

        for field in sorted(info):
            label = string.capwords(field.replace('_', ' '))
            print('{}: {}'.format(label, info[field]))

        result = 1 if state == jack.STOPPED else 0
    elif args.command == 'start':
        if state == jack.STOPPED:
            client.transport_start()
    elif args.command == 'stop':
        if state != jack.STOPPED:
            client.transport_stop()
    elif args.command == 'toggle':
        if state == jack.STOPPED:
            client.transport_start()
        else:
            client.transport_stop()
    elif args.command == 'rewind':
        client.transport_frame = 0

    client.close()
    ap.exit(result)


if __name__ == '__main__':
    main()
