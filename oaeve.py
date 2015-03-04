#!/usr/bin/env python

"""Open Annotation JSON-LD support functions for Eve."""

__author__ = 'Sampo Pyysalo'
__license__ = 'MIT'

import json

import oajson

# mapping from Eve JSON keys to JSON-LD ones
jsonld_key_rewrites = [
    ('_id', '@id'),
]

eve_to_jsonld_key_map = dict(jsonld_key_rewrites)
jsonld_to_eve_key_map = dict([(b,a) for a,b in jsonld_key_rewrites])

def eve_to_jsonld(document):
    document = oajson.remap_keys(document, eve_to_jsonld_key_map)
    oajson.add_context(document)
    oajson.add_types(document)
    return document

def eve_from_jsonld(document):
    document = oajson.remap_keys(document, jsonld_to_eve_key_map)
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
    if not is_jsonld_response(payload):
        return
    # rewrite Eve keys as JSON-LD ones
    doc = json.loads(payload.get_data())
    jsonld_doc = eve_to_jsonld(doc)
    payload.set_data(json.dumps(jsonld_doc))

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
