#!/usr/bin/env python

"""RESTful Open Annotation server based on Eve.

The RESTful Open Annotation API is primarily implemented using two
ways of modifying the Eve default API: 

1. global configuration of keys in settings.py to use OA names,
e.g. "annotatedAt" instead of the default "_created".

2. event hooks to modify incoming and outcoming documents in more
complex ways, such as removing the default "@context" value on POST
and adding it to the top-level graph on GET.
"""

__author__ = 'Sampo Pyysalo'
__license__ = 'MIT'

import sys

from eve import Eve

from settings import DEBUG
from oaeve import pre_POST_callback, post_GET_callback

app = Eve()
app.on_post_GET += post_GET_callback
app.on_pre_POST += pre_POST_callback

def main(argv):
    # TODO: don't serve directly
    app.run(host='0.0.0.0', port=5000, debug=False)
    #app.run(debug=DEBUG)
    return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
