
# coding: utf-8

# ### Data Wrangling with MongoDB: OpenStreetMap Project
# *by Gisle JT Gaasemyr*

# The primary goal of this analysis is to determine the quality of OpenStreetMap address data in the Bergen, Norway region. The main focus will be on postcode accuracy and duplicate discovery. It is not within the scope of this project to correct any errors, but rather to point out discovered errors and areas which should be investigated further.

# Before performing the analysis below, I cleaned the downloaded data file in preparation for mongodb import. I corrected incorrect postcodes and streetnames, using official government resources for quality control. For complete information about this process, see the notebook osm_data_wrangling.ipynb (html version: osm_data_wrangling.html).

# In[1]:

#importing classes from display and pretty print modules
from pprint import pprint
from IPython.display import HTML
from IPython.display import display
#importing other necessary modules and packages
import pandas as pd
from collections import defaultdict
from pymongo import MongoClient
from operator import itemgetter
import difflib
from fuzzywuzzy import fuzz
from matplotlib import pyplot as plt
import seaborn as sns

#For convenience imports are also included in individual cells where relevant


# In[2]:

#Setting up MongoDB connection
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.osm
#Creating db.bergen as a variable for the sake of brevity
bergen = db.bergen


# In[3]:

#Getting an initial overview of the data
display(HTML('<b>Count of documents in database:</b>'),bergen.count())
display(HTML('<b>First record:</b>'))
pprint(bergen.find_one())
display(HTML('<b>Document Types:</b>'))

pipeline = [ 
    { '$group': {'_id': '$type', 'count': { '$sum': 1 } } },
    {'$sort': {'count': -1 } }
]

for res in bergen.aggregate(pipeline):
    print(res['_id'],res['count'])


# In[4]:

#Ensuring no other type records, due to previous import error
bergen.find_one( {'type': {'$nin': ['way','node']} })


# In[5]:

#Creating indexes

from pymongo import ASCENDING

bergen.create_index([('address', ASCENDING),('address.street', ASCENDING),('address.housenumber', ASCENDING)])


# In[6]:

#Getting count of documents with address field

address_query = { 'address' : {'$exists' : True }}
address_documents = bergen.find(address_query)
address_count = address_documents.count()

display(HTML('<b>Number of addresses in dataset:</b>'),address_count)


# In[7]:

#Getting counts for streetnames and addresses

aggregated = bergen.aggregate([  
        {'$match' : {'address': {'$exists' : True } } },
        { "$group" : { 
                "_id" : "$address.street","count" : { "$sum" : 1} } }
    ])

household_count = 0
unique_street_count = 0
addresses_on_street = {}

for doc in aggregated:
    household_count += doc['count']
    unique_street_count += 1
    
    addresses_on_street[doc['_id']] = doc['count']

print("total addresses in Bergen:", household_count)
print("number of streetnames:", unique_street_count)


# According to January 2016 data from Statistics Norway (SSB), there are 134,328 households in Bergen. The data used by Statistics Norway is collected from the National Registry, and the data includes unit numbers for a minimum 95% of the addresses where such a number exists. The available OSM data does not contain unit numbers. Several addresses in Bergen contain multiple home units, and although the OSM data also contains non-household addresses (businesses, public institutions etc.) the number of addresses in the OSM data seems reasonable.

# Next I will take a look at the streets with the most addresses on them, to see if any of the top 10 streets are surprising, and if any of the streets have a surprisingly high number of addresses.

# In[8]:

#Taking a look at the streets with the most addresses

from operator import itemgetter

streetnames_sorted_dict = dict(sorted(addresses_on_street.items(), key=lambda x: x[1], reverse=True)[:10])
streetnames_sorted_list = sorted(addresses_on_street.items(), key=lambda x: x[1], reverse=True)


display(HTML("<b>Streets with most addresses on them:</b>"))

for street,count in streetnames_sorted_list[0:10]:
    print(street,count)


# Based on my local knowledge of the area, the list above is not very surprising. None of the streets have a higher number of addresses than I expected.

# In[9]:

#Ensuring corrected street names in cleaning script are in fact corrected in the database
for street,count in streetnames_sorted_list:
    
    if street is None:
        pass
    
    elif ('Thormøhlens' or 'Smøråshøgda 9' or 'Laguneveien 1' or 'Gate' or '.' or 'Tokanten') in street:
        #expecting 1 result
        print(street,count)


# In[10]:

#Ensuring all postcodes starting with 'NO-' are corrected. Expecting 0 results from query.
for doc in bergen.find( {'address.postcode': {'$regex': 'NO.*'} } ):
    pprint(doc['address'])
    print('----------')


# ### Misspelled street names

# In[11]:

#Checking for potential duplicate data due to misspelled street names

import difflib
from fuzzywuzzy import fuzz

def fuzzy_streets(ratio,house_count):
    
    fuzzy_matches = list()
    compare_count = 0
    
    for k1 in streetnames_sorted_list:

        if k1[0] is None:
            print("Addresses without street name:",k1[1])

        #Only comparing street names with less addresses than house_count
        elif k1[1] <= house_count:
            
            compare_count += 1

            for k2 in streetnames_sorted_list:

                if k2[0] is None:
                    pass

                elif k2[0] == k1[0]:
                    pass

                else:                    
                    
                    fuzz_ratio = fuzz.ratio(k1[0],k2[0])
                    
                    if fuzz_ratio >= ratio:
                        fuzzy_matches.append({k1: k2,"fuzz ratio": fuzz_ratio})

    print("Number of street names compared: {0} of {1}".format(compare_count,len(streetnames_sorted_list)))
    
    return fuzzy_matches


# In[12]:

#Lower than 90 fuzzy ratio gives too many false positives. Same goes for higher than 10 addresses on the street.
potential_misspellings = fuzzy_streets(92,10)


# In[13]:

potential_misspellings


# In[14]:

#Printing out the potential misspellings
import pandas as pd

df_potential_misspellings = pd.DataFrame(columns = [
        'high_spelling','high_count','low_spelling','low_count','fuzz_ratio'])

#Adding index to make it easier to sort out the items I need to investigate further
count = 0

for spellings in potential_misspellings:
    count += 1
    df_potential_misspellings.loc[count] = None
    for key, val in spellings.items():
        if type(key) == tuple:
            if key[1] > val[1]:
                df_potential_misspellings.loc[count]['high_spelling'] = key[0]
                df_potential_misspellings.loc[count]['low_spelling'] = val[0]
                df_potential_misspellings.loc[count]['high_count'] = key[1]
                df_potential_misspellings.loc[count]['low_count'] = val[1]

            else:
                df_potential_misspellings.loc[count]['high_spelling'] = val[0]
                df_potential_misspellings.loc[count]['low_spelling'] = key[0]
                df_potential_misspellings.loc[count]['high_count'] = val[1]
                df_potential_misspellings.loc[count]['low_count'] = key[1]
        else:
            df_potential_misspellings.loc[count]['fuzz_ratio'] = val

df_potential_misspellings.drop_duplicates().sort_values('high_spelling',ascending=True)


# In[15]:

df_misspelled_streets = df_potential_misspellings.loc[[18,13,1,19,6,17,2,22,9,15,12,23,10,16,3]]
df_misspelled_streets.rename(columns={ 
    'high_spelling': 'correct_name', 'low_spelling': 'wrong_name' }, inplace=True )
df_correct_spellings = df_potential_misspellings.loc[8]
df_spellings_require_research = df_potential_misspellings.loc[[4,7,5,20]]

df_misspelled_streets[['correct_name','wrong_name']].to_csv(
    'data/misspelled_streets.csv',index=False)
df_spellings_require_research.to_csv('data/research_streets_spelling.csv',index=False)


# In[16]:

df_misspelled_streets


# In[17]:

#Getting counts from db again 
for inx,name in df_misspelled_streets.iterrows():
    print(name[2],bergen.find( { 'address.street': name[2]}).count() )


# In[18]:

#Updating records
for inx,name in df_misspelled_streets.iterrows():
    bergen.update_many( { 'address.street': name[2]},
                  { '$set': {'address.street': name[0] } 
                  } )


# In[19]:

#Ensuring all is corrected. All should return count 0
for inx,name in df_misspelled_streets.iterrows():
    print(name[2],bergen.find( { 'address.street': name[2]}).count() )


# Above I have performed some QA on the street names from the Bergen OSM dataset. I have taken a closer look at the street names with less than 10 house numbers, and I have compared those street with the other street names to spot potential misspelled and duplicate street names. Based on lingual and local knowledge, I have sorted the potential misspelled streetnames into three categories: actual misspelled names, correctly spelled names and names which require more research. All 3 categories are imported to csv files, and I have corrected the actual misspelled names in the database.

# ### Duplicate addresses

# In[20]:

#Finding duplicate addresses

pipeline = [
    { '$group': { 
            '_id': { 'street': '$address.street', 'housenumber': '$address.housenumber' }, 
                'postcodes': { '$addToSet': '$address.postcode' }, 
            'count': {'$sum': 1 }
            }
        },
    { '$match': {'count': {'$gt': 1} } },
    {'$sort' : {'count' : -1} } ]


duplicate_addresses = []
duplicate_addresses_count = 0

for doc in bergen.aggregate(pipeline):
    duplicate_addresses.append(doc)
    if doc['_id'] != {}:
        duplicate_addresses_count += doc['count']

print("Number of potential duplicate addresses:", len(duplicate_addresses))
print("Documents with potential duplicate addresses:", duplicate_addresses_count)


# In[21]:

#Converting result of duplicate address query to Pandas dataframe for easier view

from pandas.io.json import json_normalize

df_duplicate_addresses = json_normalize(duplicate_addresses)

#Changing column names
df_duplicate_addresses.rename(columns={'_id.housenumber': 'housenumber','_id.street':'street'},inplace=True)
#Changing column order
df_duplicate_addresses = df_duplicate_addresses[['street', 'housenumber', 'count', 'postcodes']]

df_duplicate_addresses.head(7)


# In[22]:

#Getting some information about duplicate addresses with different postcodes

df_different_postcodes = df_duplicate_addresses[df_duplicate_addresses['postcodes'].apply(lambda x: len(x) > 1)]

# Adding column for count of postcodes for the address
df_different_postcodes = df_different_postcodes.assign(postcode_count=df_different_postcodes['postcodes'].str.len())

print('Number of duplicate addresses with different postcodes:',len(df_different_postcodes) )
print('Duplicate addresses where all the duplicates have unique postcodes:',len(
    df_different_postcodes[df_different_postcodes['count'] == df_different_postcodes['postcode_count']]))

df_different_postcodes.sort_values('postcode_count', ascending=False).head(7)


# 242 of the 914 potential duplicate addresses are likely not true duplicates, as they have unique postcodes for the address.

# In[23]:

#Function for printing individual address search results

def search_one_address(street, housenumber):
        
    query = { 'address.street': street, 'address.housenumber': {'$in': [str(housenumber),housenumber ] } }
        
    for doc in bergen.find(query):
        pprint(doc)


# In[24]:

#Looking at all documents with the top duplicate address
search_one_address('Kanalveien','66')


# In[25]:

#Looking at one of the nodes

bergen.find_one({'id': '4264197029'})


# <img src="data/kanalveien_66_duplicates.png" align="right" width="250">
# 
# Looking up the address with the most duplicates (13), Kanalveien 66, on the OpenStreetMap.org website, it becomes apparent that at least part of the reason for the many duplicates is that there are multiple business located at that address, and each business seems to have gotten its own address. 
# 
# According to the [OSM wiki](http://wiki.openstreetmap.org/wiki/Addresses#How_to_map_addresses), the policy on duplicate addresses is unclear in such cases: "However, there is still some debate on that point (see for example Address information in POI *and* building? on help.openstreetmap.org). Also, the community in some countries has established their own rules."

# In[26]:

#Function for checking individual addresses for duplicates

def duplicate_count(street,housenumber, return_list=False):
    display((HTML('<em>{0} {1}</em>'.format(street,housenumber) ) ) )
    query = { 'address.street': street, 'address.housenumber': {'$in': [str(housenumber),housenumber ] } }
    
    count = -1
    re_list = list()
    postcodes = defaultdict(int)
    
    for doc in bergen.find(query):
        count += 1
        postcodes[doc['address']['postcode']] += 1
        if return_list:
            re_list.append(doc)
    
    if count == -1:
        print("Address not found.")
    else:
        print("Duplicate records:", count)
        print("Postcodes:",dict(postcodes))
        if return_list:
            return re_list


# In[27]:

bergen.find_one( {'address.street': 'Smøråshøgda'})


# In[28]:

bergen.find_one( {'id': '334326937'})


# In[29]:

'''
Checking for duplicates among the cleaned addresses which had housenumber \
as part of the address name in the pre-cleaned file. 
'''
duplicate_count('Laguneveien',1)
duplicate_count('Smøråshøgda',9)
duplicate_count('Steinsvikvegen',430)

#For Vilhelm Bjerknesvei checking both individual addresses and range housenumber
duplicate_count('Vilhelm Bjerknesvei','4-10')
for i in range(4,11):
    duplicate_count('Vilhelm Bjerknesvei',i)


# It is not very surprising that Vilhelm Bjerknesvei 4, 6, 7 8, 9 and 10 are missing, as they are probably among the documents which were imported with address Vilhelm Bjerknesvei 4-10. It is however surprising that there are no documents with address Vilhelm Bjerknesvei 4-10 and Smøråshøgda 9. Looking at the identified misspelled street names, I see why this is: they are both among the corrected street names. I will therefore run the queries again with the corrected spellings.

# In[30]:

duplicate_count('Søråshøgda',9)
#For Vilhelm Bjerknes’ vei checking both individual addresses and range housenumber
duplicate_count("Vilhelm Bjerknes’ vei",'4-10')
for i in range(4,11):
    duplicate_count("Vilhelm Bjerknes’ vei",i)


# There are seven documents with address Vilhelm Bjerknes’ vei 4-10, and 2 documents for the individual addresses in the 4-10 range (e.g. Vilhelm Bernesvei 7). While this is a data error, only 2 of the 7 documents with address Vilhelm Bjerknesvei 4-10 are likely to be true duplicates.

# I will take a closer look at the duplicate Laguneveien 1 documents.

# In[31]:

#Searching for duplicates of Laguneveien 1

search_one_address('Laguneveien',1)


# In[32]:

pipeline = [
    { '$match': { 'address.street': 'Laguneveien' } },
    { '$group': { 
            '_id': '$address.postcode', 'count' : {'$sum': 1 } 
        } 
    },
    {'$sort' : {'count' : -1} }
    
]

for doc in bergen.aggregate(pipeline):
    pprint(doc)


# In[33]:

query = { 'address.street': 'Laguneveien', 'address.postcode': '5235', 'address.housenumber': 1 }

for doc in bergen.find(query):
    pprint(doc)


# According to The Norwegian Mapping Authority, the correct postal code for Laguneveien is 5239. The postcode for the 5235 document is incorrect.

# ### Contributors

# In[34]:

from collections import defaultdict

user_count_query = bergen.aggregate( [
   {
     '$group': {
        '_id' : { 'uid': '$created.uid', 'username': '$created.user' }
           }
        },
   {
     '$group': {
        '_id': 'null',
        'count': { '$sum': 1 }
     }
   }
] )

for doc in user_count_query:
    user_count = doc['count']

average_contributions = bergen.aggregate( [
   {
          '$group': 
            {
                '_id' : 
                { 'uid': '$created.uid', 'username': '$created.user' },
                'count': { '$sum': 1 } 
            } 
    },
    { 
            '$group': 
            {
                '_id': 'null',
                'avg': { '$avg': '$count' } 
            }
    }
] )

for doc in average_contributions:
    user_average = round(doc['avg'],2)
    
grouped_users = list(bergen.aggregate([  
        { 
            "$group" : 
            { 
                "_id" : { "uid": "$created.uid", "username": "$created.user" },
                "count" : { "$sum" : 1} 
            } 
        },
        { "$sort" : { "count" : 1 } }
        ]))

user_no = 0
halfway = round(user_count / 2)
mode_dict = defaultdict(int)

for doc in grouped_users:
        user_no += 1
        val = doc['count']
        if user_no == halfway:
            user_median = val
        
        mode_dict[val] += 1


        
user_mode = max(mode_dict.items(), key=lambda a: a[1])
mode_percentage = round((user_mode[1] / user_count) * 100,2)
            
print("Total user count:",user_count)
print("Average contributions per user:",user_average)
print("Median contributions per user:",user_median)
print("Mode of contribution count: {0} contributors ({1}%) submitted {2} edit.".format(
    user_mode[1],mode_percentage,user_mode[0] ) )



# Based on the difference between the median and the average I suspect that the OSM comunity has a few heavy contributors working on the Bergen data. To further investigate this, I will plot the data.

# In[35]:

#Creating dataframe and bins for bar chart

df_mode_dict = pd.DataFrame(pd.Series(mode_dict),columns=['count'])
df_mode_dict['contributions'] = df_mode_dict.index
df_mode_dict = df_mode_dict[['contributions','count']]

#Creating bins of various lengths
bins = list(range(0,100,10) ) + list(range(100,1000,100) ) + list(range(1000,10000,5000) ) + list(range(10000,50000,20000) ) + list(range(50000,151000,50000) )

#Generating labels for the bins
bracket_names = list()
for item in bins:
    if item != bins[-1]:
#         if item < 10:
#             bracket_names.append(str(item+1)) 
#         else:
        start = item + 1
        next = bins[bins.index(item) + 1]
        if start > 1000:
            start = str(start)[:-3] + 'K'
            next = str(next)[:-3] + 'K'
        bracket_names.append('{0} to {1}'.format(start,next))

#Assigning the bins to dataframe
categories = pd.Series(pd.cut(df_mode_dict['contributions'], bins ,
                              labels=bracket_names, include_lowest=True ) )
df_mode_dict['bracket'] = categories

display(df_mode_dict.head(3))
display(df_mode_dict.tail(3))


# In[36]:

from matplotlib import pyplot as plt
import seaborn as sns
get_ipython().magic('matplotlib inline')

for_plot = df_mode_dict.groupby('bracket')['count'].agg('sum')

fig = plt.figure(figsize=(10,4))
ax = plt.subplot(1,1,1)

#all passengers plot
rects = for_plot.plot(kind='bar',ax=ax,color='g')
ax.set_title('Contributions per user',fontsize='large',fontweight='bold')
ax.set_xlabel('Number of contributions (uneven bin sizes)',fontsize='medium')
ax.set_ylabel('User count',fontsize='medium')
ax.set_xticklabels(for_plot.index.values,rotation='70',fontsize='small')

plt.show()


# In[37]:

total_contributions = 0

for doc in grouped_users:
    try:
        total_contributions += int(doc['count'])
    except TypeError:
        pprint(doc)
    


# In[38]:

# Looking at top 10 contributors

top_users = list(bergen.aggregate([  
        { "$group" : { 
                "_id" : { "uid": "$created.uid", "username": "$created.user" },"count" : { "$sum" : 1} } },
        { "$sort" : { "count" : -1 } },
         { "$limit" : 10 }
#         { "$project" : { "_id": 0, "user": "$created.user" } } 
    ]))

for doc in top_users:
    print(doc)
    
#Calculating total user contributions for comparison
total_contributions = 0
for doc in grouped_users:
    try:
        total_contributions += int(doc['count'])
    except TypeError:
        pprint('TYPE ERROR:',doc['count'])
print('----')
print('Total contributors:',total_contributions)

total_top_10 = 0
for doc in top_users:
    total_top_10 += doc['count']

top_10_percentage = round((total_top_10/total_contributions)*100,2)

print('Total contributions by top 10 contributors: {0}, {1}%'.format(total_top_10,top_10_percentage))


# We see here that the large majority of contributions are made by a tiny portion (2.5%) of the contributing users. It seems like a lot of the contributions are automated in some way, as 3 of the top 10 usernames end in "\_import". Any potential contribution patterns these few users have is likely to heavily impact the Bergen OSM data.

# According to the address page of the OSM wiki, in mid-2014 all Norwegian official addresses were released to the public. Efforts are being made by OSM volunteers to include the released data in OSM, and the progress is being tracked using a tool called [Beebeetle](http://osm.beebeetle.com/addrnodeimportstatus.php). As of March 4, 2017, the Bergen import is listed as 99.83% complete. 1 known address duplicate is listed on the site.

# ### Other Features

# Before summing up my findings related to addresses, street names and users contributions, I'd like to take a look at the distribution of other features in the dataset.
# 
# Since mongodb is schemaless, I'll have to come up with a way to show all available variables. Since documents with types 'node and 'way' are so different from eachother, I will aggregate them separately.

# In[39]:

node_features = defaultdict(int)
node_count = 0

for doc in bergen.find({'type': 'node'}):    

    node_count += 1
    for k,v in doc.items():

        try:
            for key,val in v.items():
#             tmp_set.add(k+'_'+key)
                node_features[k+'.'+key] += 1
#         else:
        except AttributeError:
            if type(v) == list:
                for item in v:
                    if type(item) == dict:
                        for key,val in item.items():
                            node_features[k+'.'+key] += 1
                    else:
                        node_features[k] += 1
                
            elif type(v) == str:
                node_features[k] += 1
                    
print("number of node documents:",node_count)
print("Number of node feature types:",len(node_features))


# In[40]:

way_count = 0
way_features = defaultdict(int)

for doc in bergen.find( {'type': 'way'}):    

    way_count += 1
    for k,v in doc.items():

        try:
            for key,val in v.items():
#             tmp_set.add(k+'_'+key)
                way_features[k+'.'+key] += 1
#         else:
        except AttributeError:
            if type(v) == list:
                for item in v:
                    if type(item) == dict:
                        for key,val in item.items():
                            way_features[k+'.'+key] += 1
                    else:
                        way_features[k] += 1
                
            elif type(v) == str:
                way_features[k] += 1

print("number of way documents:",way_count)
print("Number of way feature types:",len(way_features))


# In[41]:

# #Commented out as it is not needed
# pipeline = [
#     {'$match': {'_type': {'$exists':1 } } },
#     {'$group': {'_id': {'type': '$type', 'feature_type':'$_type'}, 'count': {'$sum': 1 } } },
#     {'$sort': {'count': -1}}
# ]
    
# for doc in bergen.aggregate(pipeline):
#     print(doc)


# In[42]:

pprint(way_features)


# In[43]:

#Listing the way features sorted by count

for key in sorted(way_features,key=way_features.get,reverse=True):
    print(key,way_features[key])


# In[44]:

pprint(node_features)


# In[45]:

#Listing the node features sorted by count

for key in sorted(node_features,key=node_features.get,reverse=True):
    print(key,node_features[key])


# Looking at the counts of features I notice quite a few inconsistencies. For instance, I see multiple instances of website categories.

# In[46]:

print("way website features:")
for key in way_features:
    if 'url' in key or 'website' in key:
        print(key,way_features[key])
print()
print("node website features:")
for key in node_features:
    if 'url' in key or 'website' in key:
        print(key,node_features[key])


# Here at least 'website', and 'url' can probably be merged into one category. It would be beneficial to the data quality if community efforts are made to clean up inconsistent category use.

# In[47]:

#Looking for potential duplicate email feature types
print("way email features:")
for key in way_features:
    if 'email' in key:
        print(key,way_features[key])
print()
print("node email features:")
for key in node_features:
    if 'email' in key:
        print(key,node_features[key])


# In[48]:

#Ensuring there is no good reason to use 2 separate feature types for email
query = {'email': {'$exists': 1}, 'contact.email': {'$exists': 1} }

for doc in bergen.find(query):
    print(doc)


# Of the two documents which actually have both email and contact.email fields, one of them also have different email addresses listed in the different fields. Although rare, this indicates there is some value in keeping both feature types.

# ### Cuisine and eatery types

# In[49]:

#Most common food served at eatiries in Bergen

#Counts of different type of eateries
pipeline = [ 
    {'$match': {'cuisine': { '$exists': 1 } } },
    { '$group': { 
        '_id': {'cuisine': '$cuisine' }, 
        'count': {'$sum': 1 } } 
    },
    { '$sort': {'count': -1 } },
    { '$limit': 10 }
]

print("Cuisine, all eateries")
for doc in bergen.aggregate(pipeline):
    print(doc)


pipeline = [ 
    {'$match': {'amenity': 'restaurant', 'cuisine': {'$exists': 1} } },
    { '$group': { 
        '_id': {'cuisine': '$cuisine' }, 
        'count': {'$sum': 1 } } 
    },
    { '$sort': {'count': -1 } },
    { '$limit': 10 }
]
print('    ')
print("Cuisine, restaurants only")
for doc in bergen.aggregate(pipeline):
    print(doc)


# We see here that in Bergen restaurants pizza, sushi and chinese food are the top cuisines. Among all eateries with cuisine information, if we exclude coffee_shop, the top 3 cuisines are burger, pizza and sushi.

# In[50]:

#Counts of different type of eateries
pipeline = [ 
    {'$match': {'cuisine': { '$exists': 1 } } },
    { '$group': { 
        '_id': {'eatery_type': '$amenity' }, 
        'count': {'$sum': 1 } } 
    },
    {'$sort': {'count': -1 } }
]

for doc in bergen.aggregate(pipeline):
    print(doc)


# The majority of eateries with cuisine information are restaurants, cafés and fast food places.  
# Interestingly enough, 8 of the documents with cuisine information are not defined as amenities. I will take a closer look at these documents next.

# In[51]:

for doc in bergen.find({'amenity': {'$exists': 0}, 'cuisine': {'$exists': 1} } ):
    pprint(doc)
    print('   ')


# In[52]:

#Grouping documents above on shop and cuisine
pipeline = [
    { '$match': {'amenity': {'$exists': 0}, 'cuisine': {'$exists': 1} } },
    { '$group': {'_id': {'cuisine': '$cuisine', 'shop type': '$shop'}, 
                'count': {'$sum': 1 } } }
]

for res in bergen.aggregate(pipeline):
    print(res)


# All 8 of these non-eatery documents are considered shops, where 4 are bakeries and 4 are convenience shops.
# 
# Last in this section, I will generate counts of restaurants, cafės and fast food restaurants with missing cuisine information.

# In[53]:

#Counts of eatery types with cuisine information
pipeline = [ 
    {'$match': {'cuisine':{ '$exists': 1 }, 'amenity': {'$in': ['cafe','restaurant', 'fast_food'] } } },
    { '$group': { 
        '_id': {'eatery_type': '$amenity' }, 
        'count': {'$sum': 1 } } 
    },
    {'$sort': {'count': -1 } }
]

print('Eateries with cuisine information')
for doc in bergen.aggregate(pipeline):
    print(doc)

print('    ')
#Counts of eatery types without cuisine information
pipeline = [ 
    {'$match': {'cuisine':{ '$exists': 0 }, 'amenity': {'$in': ['cafe','restaurant', 'fast_food'] } } },
    { '$group': { 
        '_id': {'eatery_type': '$amenity' }, 
        'count': {'$sum': 1 } } 
    },
    {'$sort': {'count': -1 } }
]

print('Eateries missing cuisine information')
for doc in bergen.aggregate(pipeline):
    print(doc)


# Quite a few restaurants, cafés, and fast food places lack cuisine information. Community efforts should be made to improve this.

# ### Final Thoughts and summary
# 
# There are 184 address documents without street names in the dataset. Further investigation into those documents is recommended. 
# 
# To address the duplicate issue in detail, I suggest following up by looking at the individual duplicate addresses. You could for example start by looking at the three streets with the most individual duplicate addresses to see if there are any useful patterns to be found. Since a few users are very heavy contributors to the Bergen OSM data, it might also be worth searching for user patterns regarding the duplicate addresses.
# 
# I would also recommend correcting the misspelled street names, which are stored in data/misspelled_streets.csv, and conduct online research for the street names in data/research_streets_spelling.csv.
# 
# There appear to be quite a few potential duplicate fields/feature types in the dataset. Although outside the scope of this project, it would be useful to conduct further analysis and cleanup efforts of duplicate feature types.
# 
# About half of the restaurants in the dataset lack cuisine information. This could be a minimal effort task with a high yield result for the active Bergen OSM contributors.
