"""Settings for Eve and RESTful OA support functionality."""

__author__ = 'Sampo Pyysalo'
__license__ = 'MIT'

# Eve App debug setting. NOTE: this *must* be set to False for any
# publicly accessible installation, as the debugger allows arbitrary
# code execution.
DEBUG = True

# TODO: the LD_ settings really belong in oajson.py
# Default JSON-LD @context.
LD_CONTEXT = 'http://www.w3.org/ns/oa.jsonld'

# Default JSON-LD @type for items.
LD_ITEMTYPE = 'oa:Annotation'

# Default JSON-LD @type for collections. 
# TODO: make sure we want to use this spec
LD_COLLTYPE = 'http://www.w3.org/ns/hydra/core#Collection'

# Open Annotation requires xsd:dateTime (ISO 8601), such as
# "1997-07-16T19:20:30.45+01:00". TODO: time zone
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Eve HATEOAS controls are not part of JSON-LD, and partially
# rendudant with general use of link relations and URIs inherent in
# JSON-LD. However, they can be used to generate links for traversing
# paginated collections.
HATEOAS = True

# Return entire document on PUT, POST and PATCH.
#BANDWIDTH_SAVER = False

# Eve ITEMS list largely matches for the "@graph" of JSON-LD named
# graphs http://www.w3.org/TR/json-ld/#named-graphs
ITEMS = '@graph'

# Eve DATE_CREATED is essentially the same thing as oa:annotatedAt
# ("annotatedAt" for short in the @context of both OA and Web
# Annotation specs).
DATE_CREATED = 'annotatedAt'

# Eve LAST_UPDATED is NOT actually the same as oa:serializedAt, but
# the approximation is not unreasonable (think "serialized into the
# database") and so used here.
LAST_UPDATED = 'serializedAt'

# For simplicity, disable concurrency control for the moment, removing
# the "_etag" attribute and the checking for If-Match headers
# (see http://python-eve.org/features.html#concurrency)
IF_MATCH = False

# TODO: disable (setting to Null doesn't work) or rewrite '_meta'
#META = None

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

# Maximum value allowed for QUERY_MAX_RESULTS query parameter.
PAGINATION_LIMIT = 10000

# Default value for QUERY_MAX_RESULTS.
PAGINATION_DEFAULT = 10000

annotation_schema = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/nicolaiarocci/cerberus) for details.
    'body': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 1024,
    },
    'target': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 1024,
        'required': True,
    },
    'annotatedBy': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 1024,
    },
}

annotations = {
  'schema': annotation_schema,
}

DOMAIN = {
    'annotations': annotations,
}

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = 'user'
MONGO_PASSWORD = 'user'
MONGO_DBNAME = 'test'
