#!/usr/bin/env python3

"""Create a JACK client and test port-alias functionality

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
    print('unique client name generated:', client.name)

ports = client.get_ports()

print('Testing set_alias() ...')
i=0
for port in ports:
	alias_name="Alias Name %d" % i
	print("port '%s' => set_alias('%s')" % (port.shortname,alias_name))
	port.set_alias(alias_name)
	i+=1

print('Testing aliases property ...')
for port in ports:
	i=0
	for alias in port.aliases:
		print("port '%s', alias %d => '%s'" % (port.shortname,i,alias))
		i+=1

print('Testing unset_alias() ...')
i=0
for port in ports:
	alias_name="Alias Name %d" % i
	print("port '%s' => unset_alias('%s')" % (port.shortname,alias_name))
	port.unset_alias(alias_name)
	i+=1

print('Testing aliases property ...')
for port in ports:
	i=0
	for alias in port.aliases:
		print("port '%s', alias %d => '%s'" % (port.shortname,i,alias))
		i+=1
