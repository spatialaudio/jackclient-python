#!/usr/bin/env python3
"""Set/get/remove client/port metadata."""
from pprint import pprint

import jack

client = jack.Client('Metadata-Client')
port = client.inports.register('input')

client.set_property(client, jack.METADATA_PRETTY_NAME, 'Best Client Ever')
print('Client "pretty" name:',
      jack.get_property(client, jack.METADATA_PRETTY_NAME))

client.set_property(
    port, jack.METADATA_PRETTY_NAME, b'a good port', 'text/plain')
print('Port "pretty" name:',
      jack.get_property(port, jack.METADATA_PRETTY_NAME))

print('All client properties:')
pprint(jack.get_properties(client))

print('All port properties:')
pprint(jack.get_properties(port))

print('All properties:')
pprint(jack.get_all_properties())

client.remove_property(port, jack.METADATA_PRETTY_NAME)
client.remove_properties(client)
client.remove_all_properties()
