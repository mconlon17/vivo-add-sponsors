#!/usr/bin/env/python
"""
    add-sponsors.py -- From a data file consisting of sponsors of
    research, update sponsors an add sponsors

    Version 0.0 MC 2014-03-10
    --  getting started.  NOT COMPLETE

    To Do
    --  Almost everything.  Add type stuff. Read through.  Test cases. Log file.
        Exception File.  Command line args like grants. File names like grants.
        pylint.  Testing.

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.0"

__harvest_text__ = "Python Sponsors " + __version__

from vivotools import vivo_sparql_query
from vivotools import get_vivo_uri
from vivotools import assert_resource_property
from vivotools import assert_data_property
from vivotools import update_data_property
from vivotools import read_csv
from vivotools import rdf_header
from vivotools import rdf_footer
from vivotools import get_vivo_value

from datetime import datetime

def make_sponsor_dict(debug=False):
    """
    Extract all the sponsors in VIVO and organize them into a dictionary
    keyed by sponsor number value URI.
    """
    query = """
    SELECT ?uri ?number
    WHERE {
        ?uri ufVivo:sponsorNumber ?number
    }"""
    result = vivo_sparql_query(query)
    sponsor_dict = {}
    if 'results' in result and 'bindings' in result['results']:
        rows = result["results"]["bindings"]
    else:
        return sponsor_dict
    if debug:
        print query
        if len(rows) >= 2:
            print rows[0],rows[1]
        elif len(rows) == 1:
            print rows[0]
    for row in rows:
        number = row['number']['value']
        uri = row['uri']['value']
        sponsor_dict[number] = uri
    if debug:
        print sponsor_dict.items()[1:3]
    return sponsor_dict

def add_sponsor():
    """
    Add a sponsor entity.  All attributes come via update
    """
    ardf = ""
    sponsor_uri = get_vivo_uri()
    add = assert_data_property(sponsor_uri, "rdfs:label", label)
    ardf = ardf + add
    add = assert_resource_property(sponsor_uri, "rdf:type",
        "http://xmlns.com/foaf/0.1/Organization")
    ardf = ardf + add
    add = assert_resource_property(sponsor_uri, "rdf:type",
        "http://vivoweb.org/ontology/core#FundingAgency")
    ardf = ardf + add
    add = assert_data_property(sponsor_uri, "ufVivo:dateHarvested",
                                             datetime.now().isoformat())
    ardf = ardf + add
    add = assert_data_property(sponsor_uri, "ufVivo:harvestedBy",
        __harvest_text__)
    ardf = ardf + add
    return [ardf, sponsor_uri]

def update_sponsor(sponsor_uri, sponsor_data):
    """
    """
    adrf = ""
    srdf = ""
    sponsor_label = sponsor_data['NAME']
    vivo_sponsor_label = get_vivo_value(sponsor_uri, "rdfs:label")
    [add, sub] = update_data_property(sponsor_uri, "rdfs:label",
                                      vivo_sponsor_label,
                                      sponsor_label)
    ardf = ardf + add
    srdf = srdf + sub

    sponsor_number = sponsor_data['SponsorID']
    vivo_sponsor_number = get_vivo_value(sponsor_uri, "ufVivo:SponsorID")
    [add, sub] = update_data_property(sponsor_uri, "ufVivo:SponsorID",
                                      vivo_sponsor_number,
                                      sponsor_number)
    ardf = ardf + add
    srdf = srdf + sub
    
    vivo_date_harvested = get_vivo_value(sponsor_uri,
                                         "ufVivo:dateHarvested")
    [add, sub] = update_data_property(sponsor_uri, "ufVivo:dateHarvested",
                                      vivo_date_harvested,
                                      datetime.now().isoformat())
    ardf = ardf + add
    srdf = srdf + sub
    
    vivo_harvested_by = get_vivo_value(sponsor_uri, "ufVivo:harvestedBy")
    [add, sub] = update_data_property(sponsor_uri, "ufVivo:harvestedBy",
                                      vivo_harvested_by,
                                      __harvest_text__)
    ardf = ardf + add
    srdf = srdf + sub
    return [adrf, srdf]


#   Start here

print >>log_file, datetime.now(), "Start"
print >>log_file, datetime.now(), "Make sponsor dictionary"
sponsor_dict = make_sponsor_dict(debug=True)
print >>log_file, datetime.now(), "sponsor dictionary has ", \
    len(sponsor_dict), "entries"
print >>log_file, datetime.now(), "Read sponsor file"
campus = read_csv("sponsor_data.csv")
sponsors = {}
for row in campus.values():
    sponsors[row['BLDG']] = row
print >>log_file, datetime.now(), "sponsor file has ", len(sponsors.items()),
    "entries"
print >>log_file, datetime.now(), "Begin processing"
ardf = rdf_header()
srdf = rdf_header()
sponsor_found = 0
sponsor_not_found = 0
sponsor_not_in_uf_data = 0
all_numbers = sponsors.keys()
for sponsor_number in all_numbers:
    if sponsor_number not in all_numbers:
        all_numbers.append(sponsor_number)
for sponsor_number in all_numbers:
    if sponsor_number in sponsor_dict and sponsor_number in sponsors:

        # Case 1.  Sponsor in Sponsor data and VIVO. Update VIVO

        sponsor_found = sponsor_found + 1
        sponsor_uri = sponsor_dict[sponsor_number]
        [add, sub] = update_sponsor(sponsor_uri, sponsors[sponsor_number])
        ardf = ardf + add
        srdf = srdf + sub
        
                
    elif sponsor_number not in sponsor_dict:

#       Sponsor in Sponsor Data, but not in VIVO.  Add to VIVO

        sponsor_not_found = sponsor_not_found + 1
        [add, sponsor_uri] = add_sponsor()
        ardf = ardf + add
        [add, sub] = update_sponsor(sponsor_uri, sponsors[sponsor_number])
        ardf = ardf + add
        srdf = srdf + sub

    else:

#       Sponsor is only in VIVO, not in Sponsor data.  Nothing to do

        sponsor_not_in_uf_data = sponsor_not_in_uf_data + 1

print >>log_file, datetime.now(), "Found = ", sponsor_found
print >>log_file, datetime.now(), "Not Found in VIVO, will be added = ", \
    sponsor_not_found
print >>log_file, datetime.now(), "Not Found in UF data = ", \
    sponsor_not_in_uf_data
print >>log_file, datetime.now(), "Write files"
adrf = ardf + rdf_footer()
srdf = srdf + rdf_footer()
add_file = open("sponsor_add.rdf", "w")
sub_file = open("sponsor_sub.rdf", "w")
print >>add_file, adrf
print >>sub_file, srdf
add_file.close()
sub_file.close()
print datetime.now(), "Finished"
