#!/bin/bash

ROOT="http://127.0.0.1:5000"
BASE="$ROOT/annotations"

# annotation w/Open Annotation context (e.g. "hasBody" instead of "body")
curl -X POST -i -H 'Content-Type: application/json' -d '
{
  "@context": "http://www.w3.org/ns/oa.jsonld",
  "@type": "oa:Annotation",
  "hasBody": "http://example.org/foo",
  "hasTarget": "http://example.org/doc.txt#char=0,10"
}' \
    "$BASE/" | ./pretty.py

# annotation w/Web Annotation context (e.g. "body" instead of "hasBody")
curl -X POST -i -H 'Content-Type: application/json' -d '
{
  "@type": "oa:Annotation",
  "body": "http://example.org/bar",
  "target": "http://example.org/doc.txt#char=10,20"
}' \
    "$BASE/" | ./pretty.py

# annotation w/partially expanded keys (e.g. "oa:hasBody" instead of "body")
curl -X POST -i -H 'Content-Type: application/json' -d '
{
  "@context": "http://www.w3.org/ns/oa.jsonld",
  "@type": "oa:Annotation",
  "oa:hasBody": "http://example.org/baz",
  "oa:hasTarget": "http://example.org/doc.txt#char=20,30"
}' \
    "$BASE/" | ./pretty.py

# annotation w/Content-Type: application/ld+json
curl -X POST -i -H 'Content-Type: application/ld+json' -d '
{
  "@type": "oa:Annotation",
  "body": "http://example.org/quux",
  "target": "http://example.org/doc.txt#char=30,40"
}' \
    "$BASE/" | ./pretty.py

# get collection as application/json
curl -X GET -i -H 'Accept: application/json' "$BASE/" | ./pretty.py

# get collection as application/ld+json
curl -X GET -i -H 'Accept: application/ld+json' "$BASE/" | ./pretty.py

# get collection as application/rdf+xml
# curl -X GET -i -H 'Accept: application/rdf+xml' "$BASE/1"
