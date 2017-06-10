
# coding: utf-8

# In[1]:

from collections import defaultdict
from types import *


# In[2]:

#Generating sample for initial exploration. Code (minus path changes) provided by Udacity project description

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "data/bergen.osm"  # Replace this with your osm file
SAMPLE_FILE = "data/sample.osm"

k = 20 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write(b'<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write(b'</osm>')


# In[3]:

#tag count of dataset

with open('data/bergen.osm') as f:
    tree = ET.parse(f)
    root = tree.getroot()
    
    tag_dict = {}
    
    for line in root.iter():
        tag = line.tag
        
        tag_dict[tag] = tag_dict.get(tag, 0) + 1
        
    print(tag_dict)


# In[4]:

#Auditing postcode quality

OSMFILE = "data/bergen.osm"

def is_postcode(elem):
    return (elem.attrib.setdefault('k',None) == "addr:postcode")

error_postcodes = defaultdict(int)

def audit_postcodes(error_postcodes, postcode):
    
    if len(postcode) == 4:
        try:
            int(postcode)
        except TypeError:
            error_postcodes[postcode] += 1
    else:
        error_postcodes[postcode] += 1
            
def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print('{0}: {1}'.format(k, v))

def audit():
    for event, elem in ET.iterparse(OSMFILE,events=("start","end")):
#     for event, elem in ET.iterparse(OSMFILE):
        if event == 'end':
            if elem.tag in ["way","node"]:
                for tag in elem.iter("tag"):
                    if is_postcode(tag):
                        audit_postcodes(error_postcodes, tag.attrib['v'])
#             if elem.attrib.setdefault('id',None) == '21641553':
#                 for elem in elem.iter():
#                     print(elem.tag,elem.attrib)

    print_sorted_dict(error_postcodes)
    
    
audit()


# In[5]:

#Generating list of all Bergen street names as of 2005. Source: Wikipedia.

import re
import requests
from bs4 import BeautifulSoup

bergen_street_names = []

r = requests.get('https://no.wikipedia.org/wiki/Liste_over_Bergens_gater')

wiki_soup = BeautifulSoup(r.text, 'lxml')

street_div = wiki_soup.find(id='mw-content-text')

for name in street_div.find_all('li'):
    #Åstveitveien is the last name of the page, so stopping after that row to avoid bad data entries
    if name.string == 'Åstveitveien':
        bergen_street_names.append(name.string)
        break
    else:
        bergen_street_names.append(name.string)
    

#Defining search query for characters that should not be found in street names
problemchars = re.compile(r'[=\+/&<>;"\?%#$@\,:<>\t\r\n]')

#Removing incorrect items from street name list. Printing them out for transparency/QA.

count = -1

for item in bergen_street_names:
    count += 1
    if problemchars.search(item):
        print('PROBLEM STREET NAME:',item)
        print('DELETING NAME', bergen_street_names[count], 'FROM STREET NAME LIST.')
        del(bergen_street_names[count])
        


# The Wikipedia list consists of data provided by the Norwegian Mapping Authority. Since it's somewhat dated (2005), I decided to look for more publically available datasets. After a little research I discovered that the Norwegian Public Roads Administration (NPRA) has a public API which contains street name data for all of Norway.

# In[6]:

#Generating street name list from the The Norwegian Public Roads Administration API

def bergen_streets_list():
    print('Start processing 1st call')
    bergen_streets = list()
    start = None
    count = 0
    types = set()
    
    def get_bergen_streets(start=None):

        url = 'https://www.vegvesen.no/nvdb/api/v2/vegobjekter/538'

        if start:
            payload = {'inkluder': 'egenskaper', 'kommune': '1201','antall': '1000', 'start': start}
        else:
            #Hard to debug error when the initial limit was set to 1000. Lowering it to 200 works without issues.
            payload = {'inkluder': 'egenskaper', 'kommune': '1201','antall': '200'}
        headers = {'content-type': 'application/vnd.vegvesen.nvdb-v2+json'}
        r = requests.get(url, params=payload, headers=headers)

        return r


    def streets_list(start=None):

        nonlocal count
        count += 1
        response = get_bergen_streets(start)
#         global debug_response
#         debug_response = response

    #     json = get_bergen_streets()
        objects = response.json()['objekter']
        metadata = response.json()['metadata']
        print("Received batch no.",count)

        if metadata['returnert'] != 0:

            start = metadata['neste']['start']
            for object in objects:
                
                for attribute in object['egenskaper']:
                    types.add(attribute['navn'])
                    if attribute['navn'] == 'Gatenavn':
                        bergen_streets.append(attribute['verdi'])

#                     for k,v in object['egenskaper'][1].items():
#                         print(k,v)
#                     print('----------------')
            
            print("Completed processing of batch no.",count)
            streets_list(start=start)
            
    streets_list()            
    print("Attribute types:",types)
    print("Completed API calls and processing. Returning list with {} street names.".format(len(bergen_streets)))
    return bergen_streets


# In[7]:

bergen_streets = bergen_streets_list()


# In[8]:

#Checking for duplicates in the NPRA list
nrpa_set = set()

for street in bergen_streets:
    nrpa_set.add(street)
    
len(nrpa_set)


# In[9]:

#Comparing the street names from the different data providers

wikipedia_set = set(bergen_street_names)

print("Street names in the wikipedia list not found in NRPA list:",len(wikipedia_set - nrpa_set) )
print("Street names in the NRPA list not found in wikipedia list:",len(nrpa_set - wikipedia_set) )


# Next I will audit the quality of the street names in the data set. One tricky part is that Norwegian street names are concatenated with no clear distinction between the different words. For example, the equivalent of Main Street is Hovedgaten.
# 
# Due to this the main audit criteria will be whether the name exists in the Bergen street name lists sourced from the Wikipedia and NPRA.

# In[10]:

#Combining street names from both street name lists
bergen_set = nrpa_set | wikipedia_set

len(bergen_set)


# In[11]:

def lookup_street_name(streetname):
    OSMFILE = "data/bergen.osm"
    
    def is_street_name(elem):
        return (elem.attrib.setdefault('k',None) == "addr:street")

    for event, elem in ET.iterparse(OSMFILE, events=("start",)):
        if elem.tag in ("node", "way"):
            for tag in elem.iter():
                if is_street_name(tag):
                    if tag.attrib['v'] == streetname:
                        return event,elem.iter()


# In[12]:

def return_all_cities():
    OSMFILE = "data/bergen.osm"
    return_dict = defaultdict(int)
    
    def city(elem):
        return (elem.attrib.setdefault('k',None) == "addr:city")

    for event, elem in ET.iterparse(OSMFILE, events=("start",)):
        if elem.tag in ("node", "way"):
            for tag in elem.iter():
                if city(tag):
                    return_dict[tag.attrib['v']] += 1
    
    return return_dict


# In[13]:

city_count = return_all_cities()

city_count


# In[14]:

#I see some duplicates above, writing function to identify them
def find_key_duplicates(dictionary):
    keys = dictionary.keys()
    new_dict = defaultdict(int)
    for key in keys:
        new_dict[key.lower()] += 1
    
    dup_dict = dict()
    
    for key,val in new_dict.items():
        if val > 1:
            dup_dict[key] = val
            
    return dup_dict
            
        
find_key_duplicates(city_count)


# In[15]:

#Writing function to merge uppercased keys with capitalized keys
def merge_keys(dictionary):
    keys = find_key_duplicates(dictionary).keys()
    
    old_values = dict()
    
    for key in keys:
        capitalized = key.capitalize()
        uppercased =  key.upper()
        
        old_values[capitalized] = dictionary[capitalized]
        
        dictionary[key.capitalize()] = dictionary[capitalized] + dictionary[uppercased]
        del dictionary[uppercased]
        print("merged {0} value: {1}".format(capitalized,dictionary[capitalized]))

    print("old_values:",old_values)

merge_keys(city_count)


# Looking at all the cities in the dataset, it becomes clear that quite a few of them do not belong to Bergen municipality. Many, maybe most of them, do though. 
# 
# Since I am primarily focusing on Bergen I am making the decision to only clean street names within Bergen municipality. The Norwegian postal service provides a downloadble list on their website with overview of postal codes, cities and municipality they belong to.

# In[16]:

import pandas as pd

postcodes_per_municipality = pd.read_csv('data/Postnummerregister_ansi.tsv', encoding='utf-8',delimiter='\t',header=0, names=[
        'postal_code','postal_place','muni_number','muni_name','category'],
            dtype = {'postal_code': str, 'municipality_number': str})

postcodes_per_municipality.head(5)


# In[17]:

bergen_postcodes = postcodes_per_municipality[['postal_code','postal_place']][postcodes_per_municipality['muni_name'] == 'BERGEN']
bergen_postcodes['postal_place'] = bergen_postcodes['postal_place'].str.lower()


# In[18]:

bergen_postcodes.head(5)


# In[19]:

df_city_count = pd.DataFrame([city_count]).transpose()
df_city_count.index = df_city_count.index.str.lower()
df_city_count.columns = ['count']

df_city_count.sort_values('count',ascending=False)


# In[20]:

from IPython.display import display

def postal_place_clarified():

    unique_bergen = bergen_postcodes['postal_place'].unique()
    unique_norway = postcodes_per_municipality['postal_place'].str.lower().unique()

    outside_bergen = list()
    not_in_postcode_dataset = list()
    
    for val in df_city_count.index:
        
        if val not in unique_bergen:
            if val in unique_norway:
                outside_bergen.append(val)
            else:
                not_in_postcode_dataset.append(val)
        
    print('Not in Bergen:')
    display(df_city_count.loc[outside_bergen])
    print('Not found in dataset from Norway postal service:')
    display(postcodes_per_municipality[postcodes_per_municipality['postal_place'].isin(not_in_postcode_dataset)])
    print(not_in_postcode_dataset)

postal_place_clarified()


# In[21]:

osm_file = 'data/sample.osm'

# tree = ET.iterparse(osm_file, events=("start",))

tree = ET.parse(osm_file)
root = tree.getroot()


count = 0

for child in root:
    count+=1
    if count < 10:
        for tag in child:
            print(tag.attr)#.find('addr:postcode')
    else:
        break
# for event, elem in :
#         if elem.tag == "way":
#             for tag in elem.iter("tag"):
#                 if is_street_name(tag):
#                     print(elem.
#             pprint('----')
            

# def is_street_name(elem):
#     return (elem.attrib['k'] == "addr:street")
            
# def is_street_name(elem):
#     return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

# def audit():
#     for event, elem in ET.iterparse(osm_file):
#         if is_street_name(elem):
#             audit_street_type(street_types, elem.attrib['v'])    
#     print_sorted_dict(street_types) 


# In[22]:

#Creating sets to be used in next cell

bergen_pc_set = bergen_postcodes['postal_code'].values
norway_pc_set = postcodes_per_municipality['postal_code'].values


# In[23]:

#Auditing street names

from collections import defaultdict
from pprint import pprint
import re
import xml.etree.cElementTree as ET

#Auditing street names

def is_street_name(elem):
    return (elem.attrib.setdefault('k',None) == "addr:street")

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

# def is_in_bergen(elem):
#     return elem.attrib['v'] in bergen_postcodes['postal_code']

street_types = defaultdict(set)

expected = ["gate", "gaten", "vei", "veien", "veg", "vegen", "lien", "neset", "smauet", "allé",
           "høgda", "plass", "dalen", "haugen", "myra"]
expected_long = ["allmenningen", "fjorden","Flagget","Smålonane","Tangen"]

def audit_street_type(street_types, street_name):

    valid = 0
    street_type = street_name[-6::]
    
    if street_name in bergen_set:
        valid = 1
    
    else:
        for s_type in expected:

            if s_type in street_type:
                valid = 1
            else:
                for name in expected_long:
                    if street_type in name:
                        valid = 1                    

    if valid == 0:
        street_types[street_type].add(street_name)
        
        return True
    else:
        return False
            
def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print('{0}: {1}'.format(k, v))

OSMFILE = "data/bergen.osm"
bergen_streets = set()
outside_bergen = set()
outside_norway = dict()
no_postcode = list()
        
# def audit():
        
#     for event, elem in ET.iterparse(OSMFILE, events=("start",)):
# #         if elem.tag == "way":
#         if elem.tag in ("node", "way"):
#             for tag in elem.iter("tag"):
#                 if is_street_name(tag):
#                     audit_street_type(street_types, tag.attrib['v'])
#     pprint(dict(street_types))
            
def audit(osmfile):
    
    count = 0
    postcode = ''
    
    for event, elem in ET.iterparse(osmfile, events=("start",)):        
        street = ''
        postcode = ''
        
        if elem.tag in ["way", "node"]:
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    street = tag.attrib['v']
#                     street_set.add(tag.attrib['v'])
#                     street_list.append(tag.attrib['v'])
                
                if is_postcode(tag):
                    postcode = tag.attrib['v'] 
    # TO DO: Add postcode check.       
    
        if street != '':
            count += 1
            if audit_street_type(street_types, street):
                if postcode == '':
                    no_postcode.append(street)
                elif postcode in bergen_pc_set:
                    bergen_streets.add(street)
                elif postcode in norway_pc_set:
                    outside_bergen.add(street)
                else:
                    outside_norway[street] = postcode
                    
    print("Total street names audited:",count)
            
#             pprint(dict(street_types))
#     print("list:",len(street_list),"set:",len(street_set))
    print("Bergen streets (distinct):", len(bergen_streets))
    print("Outside Bergen (distinct):", len(outside_bergen))
    print("Outside Norway:", len(outside_norway))
    print("missing postcode:", len(no_postcode))
    print("Total erroneous street suffixes (mutltiple street names possible per suffix):", len(street_types))
    


# In[24]:

osmfile = "data/sample.osm"

audit(osmfile)


# In[25]:

osmfile = "data/bergen.osm"

audit(osmfile)


# In[26]:

for suffix in street_types.keys():
    street_names = street_types[suffix]
    if len(street_names) > 1:
        print(suffix, street_names)


# In[27]:


# street_types_values = set()

# for ending, names in street_types.items():
#     for street in names:
#         street_types_values.add(street)


# In[28]:

# for name in outside_bergen:
#     if name not in street_types_values:
#         print(name)


# In[29]:

# for street in street_types_values:
#     if street not in outside_bergen:
#         if street not in bergen_streets:
#             if street not in no_postcode:
#                 print(street)


# In[30]:

no_postcode


# In[31]:

bergen_streets


# In[32]:

#Street names verified through online research
verified_streets = set(['Fløttmannsplassen'])
#Names found to be outside Bergen through online research
#Also includes street names which can't be easily corrected, like post box addresses.
exclude_streets = set(['Bjelkarøyna','Holmen','P.b 139, Nesttun','Straumsåsen','Toppe Senter'])


# In[33]:

#Printing street names to be cleaned
def street_names_to_clean():
    compare_set = exclude_streets | verified_streets
    
    streets_to_clean = list()
    
    for street in bergen_streets:
        if street not in compare_set:
            streets_to_clean.append(street)
    
    return streets_to_clean
        
street_names_to_clean()


# In[34]:

#Improving names

mapping = { " Gate": " gate", " alle": " allé", "vn.": "vegen",
           "Tokanten": "Nesttunveien", "vei 4-10": "vei"
            }

def update_name(name, mapping):
#Updating street name if found key match in mapping dictionary
    for key,val in mapping.items():
        key_length =len(key)
        street_type = name[-key_length:]

        if street_type == key:
            name = re.sub(street_type,mapping[street_type],name)
            continue
    return name

def generate_new_names(street_types):

    better_names = {}
    exclude = exclude_streets | verified_streets

    
    for old_name in street_types:
        if old_name not in exclude:    

            #if old_name ends in street number, remove street number
            if re.search(' [0-9]*$',old_name):
                better_name = re.sub(' [0-9]*$','',old_name)
                print(old_name)
                print(better_name)

            else:
                better_name = update_name(old_name, mapping)
            better_names[old_name] = better_name
            
    return better_names


# In[35]:

better_names = generate_new_names(street_names_to_clean())

better_names


# Before correcting the data I will make sure the postcodes in the OSM datasets all match the list of official Norway postcodes.

# In[36]:

OSMFILE = 'data/bergen.osm'

def audit():
    
    #Creating array of official Norway postcodes
    s = postcodes_per_municipality['postal_code'].values
    count = 0
    error_count = 0
    new_errors = 0 
    
    for event, elem in ET.iterparse(OSMFILE, events=("start",)):
        if elem.tag in ["way","node"]:
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    count += 1
                    #Checking if audited postcode exists in official postcode list
                    if tag.attrib['v'] not in s:
                        error_count += 1
                        print("Erroneous postcode:", tag.attrib['v'])

                        if tag.attrib['v'] not in error_postcodes.keys():
                            new_errors += 1
                            error_postcodes[tag.attrib['v']] = 1
                        
    print("----SUMMARY---")
    print("Count of evaluated post codes:",count)
    print("Count of discovered errors:",error_count)
    print("New errors:",new_errors)
    print("--------------")
    
    #Checking whether the corrected postcodes exist in official list of Norway postcodes
    errors = 0
    for postcode in error_postcodes.keys():
        
        if postcode[-4:] not in s:
            errors += 1
            print("WARNING: {0} not in list of official postcodes!".format(postcode))
    if errors == 0:
        print("Good news! The {0} corrected postcodes exists in the official list of Norway postcodes.".        format(len(error_postcodes)))
                    
    
audit()


# Next I will write functions for making corrections based on the audit results.

# In[50]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import codecs
import json
from pprint import pprint



lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
multi_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:(.)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


# el = shape_element(element)
def shape_element(element):
    node = {}
    
    if element.tag == "node" or element.tag == "way" :
                
        node['type'] = element.tag

        created = dict()
        address = dict()
        colon_dict = dict()
        node_refs = list()
        
        for nod in element.iter():  
            tmp_hit = 0
            if element.tag == 'way' and nod.tag == 'nd':
                node_refs.append(nod.attrib['ref'])
#             if nod.tag == 'tag':
#                 if nod.attrib['k'] == 'name':
#                     print(nod.attrib.items())

            for k,v in nod.attrib.items():
#                   if v[0:4] == 'name':
#                     print(k,v)
#                     print(node)
#                     print('---')
      
                if 'k' in nod.keys():
                    node_key = nod.attrib['k']
                    node_val = nod.attrib['v']
                else:
                    node_key = ''
                    node_val = ''

#                 node_keys = nod.keys()
#                 node_vals = nod.attrib

                if problemchars.search(node_key):
                    pass

                elif re.match('addr:',node_key):
                    k_list = node_key.rstrip(':').split(':')[1:]
                    k_len =  len(k_list)
         
                    if k_len == 1:
                        #Correcting incorrect postcodes for the export file
                        if k_list[0] == 'postcode' and node_val in error_postcodes.keys():
                            address['postcode'] = node_val[-4:]
                            addr_pc = address['postcode']
                            assert isinstance(int(addr_pc), int), "postcode is not an integer: {}".format(addr_pc)
                    
                        #Correcting incorrect street names for the export file
                        elif k_list[0] == 'street' and node_val in better_names.keys():
                            address['street'] = better_names[node_val]

                            #Adding missing housenumbers
                            try:
                                address['housenumber'] = int(node_val[-1])

                            except ValueError:
                                pass

                        else:
#                             if node_val == 'NO-5035':
#                                 print('pre-change address:')
#                                 print(address)
#                                 print('k_list:',k_list)
#                                 print('k_len:',k_len)
                            address[k_list[0]] = node_val
                    elif k_len == 2 and k_list[0] == 'street':
                        pass
                    
                    elif k_len > 1:
                        print(('RECHECK ADDRESS, UNEXPECTED  VARIABLE COUNT: {0}, {1}').format(k_len,k_list))
                        print(k,v)
                        print('------------------')
                        for text in element.iter():
                            print(text.attrib.items())
                
    
                elif lower_colon.search(node_key):
                    colon_dict[node_key] = node_val
                
                #Do not remove. This is for remaining items with 'k' in key, see above for details
                elif node_key != '' and node_val != '':
                    #Ensuring type='node' and type='way' is not overwritten
                    if node_key == 'type':
                        node['_type'] = node_val
                    else:
                        node[node_key] = node_val
                    
                                
                elif k in ('k','v','ref'):
                    continue
                
#                  if v == 'name':
#                     print(k,v)
                
              
                elif k in CREATED:
                    created[k] = v

                elif k == 'lat':
                    lat = float(v)
                elif k == 'lon':
                    lon = float(v)
                    
                elif k == 'type':
                    #Ensuring type='node' and type='way' is not overwritten
                    node['_type'] = v

                else:    
                    node[k] = v
                    
                    if k == "ref":
                        print("ref",k,v)
                
#                 if node_key[0:5] == 'name:':
#                     print(node_val)
#                     print(nod.attrib)
#                     print(k,v)
#                     print(node)
#                     print('-----')

            
            if 'lat' in nod.attrib.keys():
                node['pos'] = [lat,lon]

        node['created'] = created
        
        if len(node_refs) != 0:
            node['node_refs'] = node_refs

        if len(address) != 0:
                node['address'] = {}
                for key in address.keys():
                    node['address'][key] = address[key]
        
        if len(colon_dict) > 0:
#             print(colon_dict)
            for k in colon_dict:
#                 if k[0:4] == 'name' and node['id'] == '58113331':
#                     print(k,v)
#                     print(node)
#                     print('---')
            
                k_list = k.rstrip(':').split(':')
                if len(k_list) ==  2:
                    if k_list[0] not in node:
                        node[k_list[0]] = {k_list[1] : colon_dict[k]}
                    elif type(node[k_list[0]]) == list:
                        node[k_list[0]].append({k_list[1] : colon_dict[k]})
                    else:
                        node[k_list[0]] = [ (node[k_list[0]]),{k_list[1] : colon_dict[k]} ]       
                         
#                 if k[0:4] == 'name' and node['id'] == '58113331':
#                     print('POST')
#                     print(node)
       
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    
    with codecs.open(file_out, "w") as fo:
        
        count = 0
        
        for _, element in ET.iterparse(file_in):
            
            
            count += 1
            
            if count == 100:
                print("processed 100")
            elif count == 1000:
                print("processed 1,000")
            elif count == 10000:
                print("processed 10,000")
            elif count == 100000:
                print("processed 100,000")            
            
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    #Turning off ascii control to allow Norwegian letters æøå
                    fo.write(json.dumps(el, indent=2, ensure_ascii=False)+"\n")
                else:
                    #Turning off ascii control to allow Norwegian letters æøå
                    fo.write(json.dumps(el,ensure_ascii=False) + "\n")   

    return data


# In[52]:

#process and test sample


def process_sample(input):
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map(input, False)
#     pprint(data)   
        
    correct_first_elem = {
        "id": "358065", 
        "type": "node", 
        "pos": [60.5320227, 5.2557628], 
        "created": {
            "changeset": "6007582", 
            "user": "danerikk", 
            "version": "2", 
            "uid": "114230", 
            "timestamp": "2010-10-10T22:30:34Z"
        }
    }

#     pprint(data[-10:-1])
    
    assert data[0] == correct_first_elem
    assert data[-1]["node_refs"] == [ "4504040186", "4504040035", "4504040031"] 
    
    for row in data:
        if row['id'] == "423945451":
            conrad_id_exists = 1
            assert row["address"] == {
                                    "street": "Conrad Mohrs veg", 
                                    "housenumber": "15",
                                    "city": "Bergen",
                                    "postcode": "5072"
                                      }
            assert row["node_refs"] == [ "4234494122", "4234494121",  "4234494120", "4234494119", 
                                        "4234494117", "4234494116", "4234494114", "4234494118", "4234494122"]
            
        if row['id'] == "3645588506":
            helle_id_exists = 1
            assert row["address"] == {
                                    "street": "Helleveien", 
                                    "housenumber": "34",
                                    "city": "Bergen",
                                    "postcode": "5035"
                                      }
        
#         if row['id'] in ["29099054","58113331"]:
#             pprint(row)
#             print('----')
            

    #testing ID in previous test exists
    
if __name__ == "__main__":
    process_sample('data/sample.osm')


# Next I'll create and run a function to generate the export file to be imported into MongoDB.

# In[53]:

#Process and test Bergen
def process_bergen(input):
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map(input, False)
    
    correct_first_elem = {
        "id": "358065", 
        "type": "node", 
        "pos": [60.5320227, 5.2557628], 
        "created": {
            "changeset": "6007582", 
            "user": "danerikk", 
            "version": "2", 
            "uid": "114230", 
            "timestamp": "2010-10-10T22:30:34Z"
        }
    }

    
    assert data[0] == correct_first_elem
    assert data[-1]["node_refs"] == [ "4427629468", "3984096773", "4427629467", "3984096770", 
                                     "3984252780", "3984096767", "3984187870", "3984105670", 
                                     "3984096775", "3984252779" ] 
    
    for row in data:
        if row['id'] == "423945451":
            conrad_id_exists = 1
            assert row["address"] == {
                                    "street": "Conrad Mohrs veg", 
                                    "housenumber": "15",
                                    "city": "Bergen",
                                    "postcode": "5072"
                                      }
            assert row["node_refs"] == [ "4234494122", "4234494121",  "4234494120", "4234494119", 
                                        "4234494117", "4234494116", "4234494114", "4234494118", "4234494122" ]
            
#         if row['id'] == '3645588506':
#             print("DEBUGGING")
#             print(row)
#             print("END OF DEBUG DOCUMENT")
        
        if row['id'] == "3645588506":
            helle_id_exists = 1
            assert row["address"] == {
                                    "street": "Helleveien", 
                                    "housenumber": "34",
                                    "city": "Bergen",
                                    "postcode": "5035"
                                      }   
    
    
        if row['id'] == "1652908136":
                assert row["address"]["housenumber"] == 1

        if row['id'] == "30064640":
            print("AUTOPASS")
            pprint(row)            

    #testing ID in previous test exists
    assert conrad_id_exists == 1
    assert helle_id_exists == 1
    
if __name__ == "__main__":
    process_bergen('data/bergen.osm')


# Based on the above I will not make any adjustments, as the source of one document's house number does not appear to be valuable enough to create an exception. The file is now ready for mongodb import.
