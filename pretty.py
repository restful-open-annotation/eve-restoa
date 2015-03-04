#!/usr/bin/env python

"""Pretty-print JSON response from STDIN."""

import sys
import json

for l in sys.stdin:
    if l.strip().startswith('{'):
        break
    sys.stdout.write(l)
else:
    l = ''

rest = l + sys.stdin.read()
if not rest.strip():
    sys.stdout.write(rest)
else:
    doc = json.loads(l + sys.stdin.read())
    print json.dumps(doc, sort_keys=True, indent=2, separators=(',', ': '))
