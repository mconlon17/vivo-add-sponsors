#!/usr/bin/env/python
"""
    add_sponsors.py -- From a data file consisting of sponsors of
    research, update sponsors and add sponsors

    Version 0.1 MC 2014-03-10
    --  Working as expected
    Version 0.2 MC 2014-03-16
    --  Added abbreviations, shortcuts
    Version 0.3 MC 2014-03-27
    --  Handle lang tags and datatypes in dictionary and RDF
    Version 0.4 MC 2014-03-28
    --  Handle unicode from VIVO
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.4"

__harvest_text__ = "Python Sponsors " + __version__

from vivotools import vivo_sparql_query
from vivotools import get_vivo_uri
from vivotools import assert_resource_property
from vivotools import assert_data_property
from vivotools import update_data_property
from vivotools import read_csv
from vivotools import rdf_header
from vivotools import rdf_footer
from vivotools import get_value
from vivotools import get_triples
import os
import sys

from datetime import datetime

def make_sponsor_dict(debug=False):
    """
    Extract all the sponsors in VIVO and organize them into a dictionary
    keyed by sponsor number value URI.
    """
    query = """
    SELECT ?uri ?number
    WHERE {
        ?uri ufVivo:sponsorID ?number
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
            print rows[0], rows[1]
        elif len(rows) == 1:
            print rows[0]
    for row in rows:
        number = row['number']['value']
        uri = row['uri']['value']
        sponsor_dict[number] = uri
    if debug:
        print sponsor_dict.items()[1:3]
    return sponsor_dict

def improve_sponsor_name(s):
    """
    DSP uses a series of abbreviations to sponsor names into database fields.
    Spell them out as best we can.
    """
    if s == "":
        return s
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    s = s.lower() # convert to lower
    s = s.title() # uppercase each word
    s = s + ' '   # add a trailing space so we can find these abbreviated
                  # words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace(" & ", " and ")
    t = t.replace(" &", " and ")
    t = t.replace("&", " and ")
    t = t.replace("/", " @")
    t = t.replace("/", " @") # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace(",", " !") # might be two commas in input
    t = t.replace("-", " #")
    t = t.replace("Acad ", "Academy ")
    t = t.replace("Adm ", "Administration ")
    t = t.replace("Admn ", "Administration ")
    t = t.replace("Ag ", "Agriculture ")
    t = t.replace("Agcy ", "Agency ")
    t = t.replace("Agri ", "Agricultural ")
    t = t.replace("Am ", "American ")
    t = t.replace("Amer ", "American ")
    t = t.replace("And ", "and ")
    t = t.replace("Asso ", "Association ")
    t = t.replace("Assoc ", "Association ")
    t = t.replace("Bd ", "Board ")
    t = t.replace("Brd ", "Board ")
    t = t.replace("Bur ", "Bureau ")
    t = t.replace("Bwxt ", "BWXT ")
    t = t.replace("Char ", "Charitable ")
    t = t.replace("Cncl ", "Council ")
    t = t.replace("Cntr ", "Center ")
    t = t.replace("Cnty ", "County ")
    t = t.replace("Co ", "Company ")
    t = t.replace("Coll ", "College ")
    t = t.replace("Corp ", "Corporation ")
    t = t.replace("Ctr ", "Center ")
    t = t.replace("Dept ", "Department ")
    t = t.replace("Dev ", "Development ")
    t = t.replace("Edu ", "Education ")
    t = t.replace("Fed ", "Federal ")
    t = t.replace("Fl ", "Florida ")
    t = t.replace("For ", "for ")
    t = t.replace("Fdtn ", "Foundation ")
    t = t.replace("Fou ", "Foundation ")
    t = t.replace("Gov ", "Government ")
    t = t.replace("Hlth ", "Health ")
    t = t.replace("Hosp ", "Hospital ")
    t = t.replace("Hsp ", "Hospital ")
    t = t.replace("Inst ", "Institute ")
    t = t.replace("Intl ", "International ")
    t = t.replace("Md ", "MD ")
    t = t.replace("Med ", "Medical ")
    t = t.replace("Mem ", "Memorial ")
    t = t.replace("Mgmt ", "Management ")
    t = t.replace("Nat ", "Natural ")
    t = t.replace("Natl ", "National ")
    t = t.replace("Of ", "of ")
    t = t.replace("Ofc ", "Office ")
    t = t.replace("On ", "on ")
    t = t.replace("Reg ", "Regional ")
    t = t.replace("Res ", "Research ")
    t = t.replace("Sci ", "Science ")
    t = t.replace("Se ", "Southeast ")
    t = t.replace("Soc ", "Society ")
    t = t.replace("Tech ", "Technology ")
    t = t.replace("Univ ", "University ")
    t = t.replace("Us ", "US ")
    t = t.replace(" @", "/") # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" #", "-") # restore -
    return t[:-1] # Take off the trailing space

def add_sponsor(sponsor_id):
    """
    Add a sponsor entity.  All attributes come via update
    """
    ardf = ""
    sponsor_uri = get_vivo_uri()
    add = assert_resource_property(sponsor_uri, "rdf:type",
        "http://xmlns.com/foaf/0.1/Organization")
    ardf = ardf + add
    add = assert_resource_property(sponsor_uri, "rdf:type",
        "http://vivoweb.org/ontology/core#FundingOrganization")
    ardf = ardf + add
    add = assert_data_property(sponsor_uri, "ufVivo:sponsorID",
        sponsor_id)
    ardf = ardf + add
    return [ardf, sponsor_uri]

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

def update_org_types(org_uri, org_string):
    """
    Given a VIVO org URI and collection of sponsor types, create add and
    sub RDF to update the VIVO org types
    """
    org_okay = ['http://xmlns.com/foaf/0.1/Organization',
                'http://www.w3.org/2002/07/owl#Thing',
                'http://xmlns.com/foaf/0.1/Agent']
    org_letters = {
        'A': 'http://vivoweb.org/ontology/core#Association',
        'C': 'http://vivoweb.org/ontology/core#Company',
        'U': 'http://vivoweb.org/ontology/core#University',
        'B': 'http://vivoweb.org/ontology/core#Laboratory',
        'S': 'http://vivoweb.org/ontology/core#School',
        'M': 'http://vivoweb.org/ontology/core#Museum',
        'Y': 'http://vivoweb.org/ontology/core#Library',
        'H': 'http://vivoweb.org/ontology/core#Publisher',
        'T': 'http://vivoweb.org/ontology/core#Center',
        'E': 'http://vivoweb.org/ontology/core#College',
        'X': 'http://vivoweb.org/ontology/core#ExtensionOrganization',
        'V': 'http://vivoweb.org/ontology/core#Division',
        'P': 'http://vivoweb.org/ontology/core#Program',
        'D': 'http://vivoweb.org/ontology/core#Department',
        'F': 'http://vivoweb.org/ontology/core#Foundation',
        'N': 'http://vivoweb.org/ontology/core#FundingOrganization',
        'R': 'http://vivoweb.org/ontology/core#ResearchOrganization',
        'G': 'http://vivoweb.org/ontology/core#GovernmentAgency',
        'I': 'http://vivoweb.org/ontology/core#Institute',
        'L': 'http://vivoweb.org/ontology/core#ClinicalOrganization'
        }

    ardf = ""
    srdf = ""
    vivo_types = get_types(org_uri)
    org_types = []
    for org_char in org_string:
        if org_char in org_letters:
            org_types.append(org_letters[org_char])

    for org_type in vivo_types:
        if (len(org_types) == 0 or org_type not in org_types) and \
            org_type not in org_okay:
            sub = assert_resource_property(org_uri, "rdf:type", org_type)
            srdf = srdf + sub
    for org_type in org_types:
        if len(vivo_types) == 0 or org_type not in vivo_types:
            add = assert_resource_property(org_uri, "rdf:type", org_type)
            ardf = ardf + add
    return [ardf, srdf]

def update_sponsor(sponsor_uri, sponsor_data):
    """
    Given the VIVO URI of a sponsor and a dictionary of sponsor data,
    update the attrbutes in VIVO with the data from the dictionary

    To Do:

    Process type assertions
    """
    ardf = ""
    srdf = ""
    vivo_sponsor_label = get_value(sponsor_uri, "rdfs:label")
    [add, sub] = update_data_property(sponsor_uri, "rdfs:label",
                                      vivo_sponsor_label,
                                      sponsor_data['sponsor_label'])
    ardf = ardf + add
    srdf = srdf + sub

    [add, sub] = update_org_types(sponsor_uri, \
        sponsor_data['SponsorTypes']+'N')
    ardf = ardf + add
    srdf = srdf + sub

    if ardf != "" or srdf != "":

        vivo_date_harvested = get_value(sponsor_uri,
                                             "ufVivo:dateHarvested")
        [add, sub] = update_data_property(sponsor_uri, "ufVivo:dateHarvested",
                                          vivo_date_harvested,
                                          datetime.now().isoformat())
        ardf = ardf + add
        srdf = srdf + sub

        vivo_harvested_by = get_value(sponsor_uri, "ufVivo:harvestedBy")
        [add, sub] = update_data_property(sponsor_uri, "ufVivo:harvestedBy",
                                          vivo_harvested_by,
                                          __harvest_text__)
        ardf = ardf + add
        srdf = srdf + sub
    return [ardf, srdf]


#   Start here

if len(sys.argv) > 1:
    dsp_file_name = str(sys.argv[1])
else:
    dsp_file_name = "test_sponsor_data.txt"
file_name, file_extension = os.path.splitext(dsp_file_name)

add_file = open(file_name+"_add.rdf", "w")
sub_file = open(file_name+"_sub.rdf", "w")
log_file = open(file_name+"_log.txt", "w")

print >>log_file, datetime.now(), "Start"
print >>log_file, datetime.now(), "Make sponsor dictionary"
sponsor_dict = make_sponsor_dict(debug=True)
print >>log_file, datetime.now(), "sponsor dictionary has ", \
    len(sponsor_dict), "entries"
print >>log_file, datetime.now(), "Read sponsor file"
uf_sponsors = read_csv(dsp_file_name)
sponsors = {}
for row in uf_sponsors.values():
    row['sponsor_label'] = improve_sponsor_name(row['SponsorName'])
    sponsors[row['SponsorID']] = row
print >>log_file, datetime.now(), "sponsor file has ", len(sponsors.items()),\
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
        [add, sponsor_uri] = add_sponsor(sponsor_number)
        ardf = ardf + add
        [add, sub] = update_sponsor(sponsor_uri, sponsors[sponsor_number])
        ardf = ardf + add
        srdf = srdf + sub

    else:

#       Sponsor is only in VIVO, not in Sponsor data.  Nothing to do

        sponsor_not_in_uf_data = sponsor_not_in_uf_data + 1

print >>log_file, datetime.now(), "Found in VIVO =", sponsor_found, " will be updated"
print >>log_file, datetime.now(), "Not Found in VIVO =", \
    sponsor_not_found, " will be added"
print >>log_file, datetime.now(), "Found only in VIVO =", \
    sponsor_not_in_uf_data, "No action to be taken"
print >>log_file, datetime.now(), "Write files"
adrf = ardf + rdf_footer()
srdf = srdf + rdf_footer()
print >>add_file, adrf.encode('ascii','xmlcharrefreplace')
print >>sub_file, srdf.encode('ascii','xmlcharrefreplace')
add_file.close()
sub_file.close()
print >>log_file, datetime.now(), "Finished"
