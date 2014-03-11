#!/usr/bin/env/python
"""
    test_get_types.py -- test get_types

    Version 0.1 MC 2013-12-27
    --  Initial version.
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2014, University of Florida"
__license__     = "BSD 3-Clause license"
__version__     = "0.1"

from vivotools import get_triples
from datetime import datetime

def get_types(uri):
    """
    Given a VIVO URI, return its types
    """
    types = []
    triples = get_triples(uri)
    if 'results' in triples and 'bindings' in triples['results']:
        rows = triples['results']['bindings']
        for row in rows:
            p = row['p']['value']
            o = row['o']['value']
            if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                types.append(o)
    return types

print datetime.now(), "Start"
print get_types("http://vivo.ufl.edu/individual/n25562")
print get_types("http://vivo.ufl.edu/individual/n4820")
print get_types("http://vivo.ufl.edu/individual/n471753241")
print datetime.now(), "Finish"
