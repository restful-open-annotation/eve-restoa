#!/usr/bin/env python

"""Open Annotation JSON-LD support functions for Eve."""

__author__ = 'Sampo Pyysalo'
__license__ = 'MIT'

import json
import urlparse

import flask

import oajson

# whether to expand @id values to absolute URLs
ABSOLUTE_ID_URLS = True

# mapping from Eve JSON keys to JSON-LD ones
jsonld_key_rewrites = [
    ('_id', '@id'),
]

eve_to_jsonld_key_map = dict(jsonld_key_rewrites)
jsonld_to_eve_key_map = dict([(b,a) for a,b in jsonld_key_rewrites])

def eve_to_jsonld(document):
    document = oajson.remap_keys(document, eve_to_jsonld_key_map)
    if ABSOLUTE_ID_URLS:
        ids_to_absolute_urls(document)
    oajson.add_context(document)
    oajson.add_types(document)
    remove_meta(document)
    rewrite_links(document)
    return document

def eve_from_jsonld(document):
    document = oajson.remap_keys(document, jsonld_to_eve_key_map)
    # TODO: invert ids_to_absolute_urls() here
    oajson.normalize(document)
    oajson.remove_context(document)
    oajson.remove_types(document)
    return document

def is_jsonld_response(response):
    """Return True if the given Response object should be treated as
    JSON-LD, False otherwise."""
    # TODO: reconsider "application/json" here
    return response.mimetype in ['application/json', 'application/ld+json']

def post_GET_callback(resource, request, payload):
    """Event hook to run after executing a GET method.

    Converts Eve payloads that should be interpreted as JSON-LD into
    the Open Annotation JSON-LD representation.
    """
    if not is_jsonld_response(payload):
        return
    doc = json.loads(payload.get_data())
    jsonld_doc = eve_to_jsonld(doc)
    payload.set_data(json.dumps(jsonld_doc))

def _collection_ids_to_absolute_urls(document):
    """Rewrite @id values from relative to absolute URL form for collection."""
    for item in document.get(oajson.ITEMS, []):
        _item_ids_to_absolute_urls(item)

def _item_ids_to_absolute_urls(document):
    """Rewrite @id values from relative to absolute URL form for item."""
    id_ = document['@id']
    base = flask.request.base_url
    document['@id'] = urlparse.urljoin(base, id_)

def ids_to_absolute_urls(document):
    """Rewrite @id value from relative to absolute URL form."""
    if oajson.is_collection(document):
        return _collection_ids_to_absolute_urls(document)
    else:
        return _item_ids_to_absolute_urls(document)

def remove_meta(document):
    """Remove Eve pagination meta-information ("_meta") from request
    if present."""
    try:
        del document['_meta']
    except KeyError:
        pass

def _rewrite_collection_links(document):
    """Rewrite Eve HATEOAS-style "_links" to JSON-LD for a collection.

    Also rewrites links for items in the collection."""
    links = document.get('_links')
    assert links is not None, 'internal error'

    # Eve generates RFC 5988 link relations ("next", "prev", etc.)
    # for collections when appropriate. Move these to the collection
    # level.
    for key in ['start', 'last', 'next', 'prev', 'previous']:
        if key not in links:
            pass
        elif 'href' not in links[key]:
            print 'Warning: no href in Eve _links[%s]' % key
        else:
            assert key not in document, \
                'Error: redundant %s links: %s' % (key, str(document))
            # TODO: don't assume the RESTful OA keys match Eve ones. In
            # particular, consider normalizing 'prev' vs. 'previous'.
            document[key] = links[key]['href']

    # Others assumed to be redundant with JSON-LD information and safe
    # to delete.
    del document['_links']

    # Process _links in collection items. (At the moment, just
    # delete them.)
    for item in document.get(oajson.ITEMS, []):
        try:
            del item['_links']
        except KeyError:
            pass

    return document

def _rewrite_item_links(document):
    """Rewrite Eve HATEOAS-style "_links" to JSON-LD for non-collection."""
    links = document.get('_links')
    assert links is not None, 'internal error'

    # Eve is expected to provide "collection" as a refererence back to
    # the collection of which the item is a member. We'll move this to
    # the item level with the collection link relation (RFC 6573)
    if 'collection' not in links or 'href' not in links['collection']:
        print 'Warning: no collection in Eve _links.' # TODO use logging
    else:
        assert oajson.COLLECTION_KEY not in document, \
            'Error: redundant collection links: %s' % str(document)
        document[oajson.COLLECTION_KEY] = links['collection']['href']

    # Eve also generates a "self" links, which is redundant with
    # JSON-LD "@id", and "parent", which is not defined in the RESTful
    # OA spec. These can simply be removed.
    del document['_links']
    return document

def rewrite_links(document):
    """Rewrite Eve HATEOAS-style "_links" to JSON-LD."""
    # HATEOAS is expected but not required, so _links may be absent.
    if not '_links' in document:
        print "Warning: no _links in Eve document." # TODO use logging
        return document
    if oajson.is_collection(document):
        return _rewrite_collection_links(document)
    else:
        return _rewrite_item_links(document)

def is_jsonld_request(request):
    """Return True if the given Request object should be treated as
    JSON-LD, False otherwise."""
    content_type = request.headers['Content-Type'].split(';')[0]
    # TODO: reconsider "application/json" here
    return content_type in ['application/json', 'application/ld+json']

def rewrite_content_type(request):
    """Rewrite JSON-LD content type to assure compatibility with Eve.""" 
    if request.headers['Content-Type'].split(';')[0] != 'application/ld+json':
        return # OK
    # Eve doesn't currently support application/ld+json, so we'll
    # pretend it's just json by changing the content-type header.
    # werkzeug EnvironHeaders objects are immutable and disallow
    # copy(), so hack around that. (This is probably a bad idea.)
    headers = { key: value for key, value in request.headers }
    parts = headers['Content-Type'].split(';')
    if parts[0] == 'application/ld+json':
        parts[0] = 'application/json'
    headers['Content-Type'] = ';'.join(parts)
    request.headers = headers

def pre_POST_callback(resource, request):
    # force=True because older versions of flask don't recognize the
    # content type application/ld+json as JSON.
    doc = request.get_json(force=True)
    assert doc is not None, 'get_json() failed for %s' % request.mimetype
    # NOTE: it's important that the following are in-place
    # modifications of the JSON dict, as assigning to request.data
    # doesn't alter the JSON (it's cached) and there is no set_json().
    doc = eve_from_jsonld(doc)
    # Also, we'll need to avoid application/ld+json.
    rewrite_content_type(request)
