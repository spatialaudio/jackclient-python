#!/usr/bin/env python3

"""Create a JACK client and test port-alias functionality.

This client test the 3 functions related with port-aliases

"""

import jack

print('starting TestAlias client')

client = jack.Client('TestAlias')

if client.status.server_started:
    print('JACK server was started')
else:
    print('JACK server was already running')
    if client.status.name_not_unique:
        print('unique client name generated: {}'.format(client.name))

ports = client.get_ports()

print('Testing set_alias() ...')
for i, port in enumerate(ports):
    alias_name = 'Alias Name {}'.format(i)
    print("port '{}' => set_alias('{}')".format(port.shortname,alias_name))
    port.set_alias(alias_name)

print('Testing aliases property ...')
for port in ports:
    for i, alias in enumerate(port.aliases):
        print("port '{}', alias {} => '{}'".format(port.shortname,i,alias))

print('Testing unset_alias() ...')
for i, port in enumerate(ports):
    alias_name = 'Alias Name {}'.format(i)
    print("port '{}' => unset_alias('{}')".format(port.shortname,alias_name))
    port.unset_alias(alias_name)

print('Testing aliases property ...')
for port in ports:
    for i, alias in enumerate(port.aliases):
        print("port '{}', alias {} => '{}'".format(port.shortname,i,alias))
