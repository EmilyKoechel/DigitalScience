# -*- coding: utf-8 -*-
"""Starter Kit 09292023

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q6d9Ttv7EeylwZTbfQFvmKSn5rFSYjqB

##Resources:
"""

##Helpful resources:
##  API Data Sources and Field names: https://docs.dimensions.ai/dsl/data-sources.html
##  API and DSL Documentation: https://docs.dimensions.ai/dsl/index.html
##  API Lab ("Cookbooks" for common use cases such as citation analysis): https://api-lab.dimensions.ai/
##  DIMCLI Documentation (also some non-Colab options here): https://digital-science.github.io/dimcli/getting-started.html

##   Please contact me if I can be of further help.  I'm happy to support your data pulls for a specific analysis
##   or help you with automation on commonly used datasets pulled from the API.
##   Emily Koechel, Technical PSM, Boulder, Colorado -- e.koechel@digital-science.com
##   Schedule time:  https://calendar.app.google/be2NxPDvo1EiLjCa6
##Check for updated versions of this StarterKit: https://github.com/EmilyKoechel/DigitalScience

"""##Python Prep and API Connection"""

#Install necessary libraries and packages:
!pip install requests
!pip install dimcli -U
!pip install pandasql
import requests
import datetime
import dimcli
from dimcli.utils import *
import json
import sys
import pandas as pd
import numpy as np
from pandasql import sqldf
import pandasql as ps
dimcli
dsl = dimcli.Dsl()
print("==\nCHANGELOG\nThis notebook was last run on %s\n==" % datetime.date.today().strftime('%b %d, %Y'))

#CONNECT TO THE DIMENSIONS API:
from google.colab import drive
drive.mount('/content/drive')
file_path = "/content/drive/My Drive/APIKeys.csv" #Be sure this location is ONLY accessible by you.
API = pd.read_csv(file_path)
MY_KEY = API.at[0, 'DimensionsKey']
dimcli.login(key=MY_KEY, endpoint="https://app.dimensions.ai")
#One-time Preparation instructions:
#   Create a .csv file in your Google Drive named "APIKeys.csv"
#   In cell A1, type "DimensionsKey"  (No quotation marks)
#   In cell A2, type your secret API key (Find under "My Account" in the webapp)


##ALTERNATIVELY, Hard Code your Key - Please do not share your code if it contains a visible API key
##    type your key into the space below between double quotes:
##dimcli.login(key="YOUR KEY HERE", endpoint="https://app.dimensions.ai")

"""##Simple calls with Magic and dimcli"""

#  %dsldf = single line query with up to 1000 records returned (Full count provided)
#  %%dsldf = Multiline query with up to 1000 records returned (Full count provided)
#  %dslloopdf = single line query with up to 50000 records returned (Full count provided)
#  %%dslloopdf = Multiline query with up to 50000 records returned (Full count provided)
#Magic using "%%" must be the only code in the cell with no comments preceding it

#Below are four ways of creating a Dataframe named DF_Octopus

#These THREE calls will return the same results:

#Dimcli:
DF_Octopus = dsl.query(f"""search publications for "octopus"
                                     return publications limit 500""", verbose=True).as_dataframe()
DF_Octopus.head(100)

#Magic 1-line:
DF_Octopus = %dsldf search publications for "octopus" return publications limit 500
DF_Octopus.head(9)

#Magic multi-line (next cell)

# Commented out IPython magic to ensure Python compatibility.
# %%dsldf DF_Octopus
# search publications
# for "Octopus"
# return publications limit 500

# Commented out IPython magic to ensure Python compatibility.
# %%dsldf DF_Octopus
# search publications
# for "Octopus"
# return publications limit 500

#These THREE calls will return the same results:

#Dimcli:
DF_Octopus = dsl.query_iterative(f"""search publications
                              for "octopus" where year in [2015:2020]
                              return publications""", verbose=True).as_dataframe()
DF_Octopus.head(100)

#Magic 1-line:
DF_Octopus = %dslloopdf search publications for "octopus" where year in [2015:2020] return publications


#Magic multi-line (next cell)

# Commented out IPython magic to ensure Python compatibility.
# %%dslloopdf DF_Octopus
# search publications
# for "Octopus"
# where year in [2015:2020]
# return publications[id+title+doi+authors+research_orgs]

"""##Dataframe return options with Dimcli:"""

#Each option returns different default views providing exploded details

DF_Octopus = dsl.query(f"""search publications for "octopus"
                           return publications[id+concepts_scores+authors]
                           limit 500""", verbose=True).as_dataframe()
DF_Octopus.head(100)

DF_Octopus = dsl.query(f"""search publications for "octopus"
                           return publications[id+concepts_scores+authors]
                           limit 500""", verbose=True).as_dataframe_authors()
DF_Octopus.head(100)

DF_Octopus = dsl.query(f"""search publications for "octopus"
                           return publications[id+concepts_scores+authors]
                           limit 500""", verbose=True).as_dataframe_authors_affiliations()
DF_Octopus.head(100)

DF_Octopus = dsl.query(f"""search publications for "octopus"
                           return publications[id+concepts_scores]
                           limit 500""", verbose=True).as_dataframe_concepts()
DF_Octopus.head(100)

"""##Export to CSV"""

## Prepare your dataframe for analysis in another tool such as Tableau, PowerBI or Excel.

#Make API call(s)
Octopus20082017 = %dslloopdf search publications for "Octopus" where year in [2008:2017] and authors_count < 200 return publications[id+title+doi+unnest(authors)]
Octopus20182022 = %dslloopdf search publications for "Octopus" where year in [2018:2022] and authors_count < 200 return publications[id+title+doi+unnest(authors)]

#OPTIONAL:  Manipulate results with Pandas/Python:
# In this case, we are combining the two calls above and then dropping any non-corresponding authors
Octopus = pd.concat([Octopus20082017, Octopus20182022])
Octopus = Octopus[(Octopus['authors.corresponding']) == True]
Octopus.head(9)

#Export to CSV on Google Drive
from google.colab import drive
drive.mount('/content/drive')
path = '/content/drive/My Drive/PythonTestingStuff/Octopus.csv'  ##Edit accordingly
with open(path, 'w', encoding = 'utf-8-sig') as f:
  Octopus.to_csv(f)

## Jupyter and other options look here: https://digital-science.github.io/dimcli/getting-started.html

"""##ForLoop Method (Pull more than 50K records)

"""

#Each loop (Example "Animal Sciences 2022" must return fewer than 50K results
#The results of each loop are concatenated into a single dataset for further analysis/manipulation

dsl = dimcli.Dsl()
YearList=list(range(2021,2023))
KWList = (['Animal Sciences','wind energy'])
print("Keyword List: ",KWList)

BigSet=pd.DataFrame()
for k in KWList:
  for y in YearList:
    print("****************Loop:",k,y,"*****************************************")
    PubChunk =  %dslloopdf search publications in title_abstract_only for "\"{k}\"" where year = {y} return publications[id]
    PubChunk['SearchTerm'] = k
    BigSet = pd.concat([BigSet, PubChunk])
    print("1 second pause for API Rest")
    time.sleep(1) # Seconds
    print("Running total records in BigSet:  ",len(BigSet))
BigSet.head(9)

"""##List Chunk Method (Pull more than 50K records)"""

# Using any Pandas list (which can be quite long!), search for chunks of that list iteratively
# and append results together into a single dataset

#This example will return all the information about the publications that cited the Pubs we identified in the prior call.
#Dedupe and drop nulls; create a list of the interesting publications we found above
PubList = BigSet['id'].dropna().tolist()
PubList = list(dict.fromkeys(PubList))

print(PubList)

ChunkNumber = 1
ChunkSize = 400  #<--  If you get an error, reduce this number.  Max is 500; 200 is a great starting point.
TotalChunks = round(0.5+(len(PubList)/ChunkSize))
# Find publications that cited the list above
q = """search publications where referenced_pubs in {}
              return publications[id+year+date+title+journal+abstract+category_for+doi
              +times_cited+altmetric+field_citation_ratio+relative_citation_ratio+recent_citations
              +reference_ids+linkout+open_access]"""
results = []
for chunk in (list(chunks_of(list(PubList), ChunkSize))):
    print("Working on Chunk #",(ChunkNumber)," of ",TotalChunks)
    ChunkNumber = ChunkNumber+1
    data = dsl.query_iterative(q.format(json.dumps(chunk)), verbose=False)
    results += data.publications
    time.sleep(1)
Pubs = pd.DataFrame().from_dict(results)
print("Publications found: ", len(Pubs))
Pubs.drop_duplicates(subset='doi', inplace=True)
print("Unique publications found: ", len(Pubs))
Pubs.head(5)

"""## Pull, Explode and Flatten; Identify Author Order

Goal: Identify the publications where a researcher from My Institution or a Peer institution is a First or Last Author; create a flattened table for further analysis in Excel, PowerBI, Tableau, or the like
"""

#Create a Python Function that can be run against any nested repeated field returned by the API:
def explode_nested_repeated_field(dataframe, field_name):
    exploded_df = (dataframe.explode(field_name).reset_index(drop=True))
    normalized_df = pd.json_normalize(exploded_df[field_name])
    normalized_df.columns = [field_name + '_' + col for col in normalized_df.columns]
    dataframe = pd.concat([exploded_df.drop(columns=[field_name]), normalized_df], axis=1)
    return dataframe

dsl = dimcli.Dsl()

#Call the API and return data to a Dataframe; some fields will contain nested, repeated values
CALL = dsl.query_iterative("""search publications
                    in title_abstract_only for "neuroscience" or for "glioma"
                    where year in [2000:2022] and research_orgs in ["grid.21925.3d","grid.147455.6","grid.25879.31","grid.29857.31"]
                    return publications[id+title+year+times_cited+authors+open_access+authors_count+journal]""", verbose=True).as_dataframe()  ##researcher_id, pub_id, current_organization_ID

ONCOLOGY = CALL.rename({'id':'PubID'}, axis=1)

ONCOLOGY = explode_nested_repeated_field(ONCOLOGY, 'authors')
ONCOLOGY['AuthorNumber'] = ONCOLOGY.groupby(['PubID']).cumcount()+1;
ONCOLOGY = explode_nested_repeated_field(ONCOLOGY, 'authors_affiliations')
#Clear up dupes taking only the first Raw Affiliation record
ONCOLOGY = ONCOLOGY.drop_duplicates(subset=['PubID','authors_researcher_id','authors_last_name','authors_first_name',
                                       'authors_affiliations_id','authors_affiliations_name'], keep="first", inplace=False)

ONCOLOGY=ONCOLOGY.explode('open_access').reset_index()                  # Open_access is repeated, but not nested. It only needs to be exploded:
ONCOLOGY = ONCOLOGY[ONCOLOGY.open_access != "oa_all"]                   # To analyze by gold vs. closed vs. green, etc.
#ONCOLOGY = ONCOLOGY[ONCOLOGY.open_access.isin(["oa_all", "closed"])]   # To analyze by open vs closed

#Identify First and Last Authors (Be sure you haven't filtered Dataframe to this point!)
ONCOLOGY['AuthorCategory'] = np.where(
     ONCOLOGY['AuthorNumber']==1,
    'FirstAuthor',
     np.where(
        (ONCOLOGY['authors_count']-ONCOLOGY['AuthorNumber'])==0,"LastAuthor",""
     )
)

#Keep only records flagged as First or Last Author:
ONCOLOGY = ONCOLOGY[(ONCOLOGY["AuthorCategory"].isin(['LastAuthor','FirstAuthor']))]
#Keep only records where the author is my my institution or a peer institution:
ONCOLOGY = ONCOLOGY[(ONCOLOGY["authors_affiliations_id"].isin(["grid.21925.3d","grid.147455.6","grid.25879.31","grid.29857.31"]))]

ONCOLOGY.head(9)

"""##Multi-Level Grouping"""

# For counts when you don't need publication-level detail:
# Combine Python For Loops with DSL Aggregations to get data at any level.
# Add additional loops as needed
dsl = dimcli.Dsl()

#Make lists to use in FOR LOOPs

#OAList = ['closed', 'oa_all', 'gold', 'bronze', 'green', 'hybrid']
#Alternatively, use the API to write your lists to ensure completeness and avoid typos:
OA = %dsldf search publications return open_access
OAList = list(dict.fromkeys(OA['id'].dropna().tolist()))
print(OAList)

CF = %dsldf search publications return category_for limit 1000
CF = (CF[CF['id'] < '80024']).sort_values(by=['id']) #Limit to 2-digit FOR Codes
CFList = list(dict.fromkeys(CF['id'].dropna().tolist()))
print(CFList)

#YearList=list(range(2000,2023))

#TestingLists: (Delete  / comment out after testing)
OAList = ['closed', 'green', 'hybrid']
CFList = ['80001', '80002', '80003', '80004', '80005']

#This example Aggregates by year - use your longest facetable list (Up to 1000) as the DSL aggregate level .
BigSet=pd.DataFrame()
for o in OAList:
  for c in CFList:
      QUERY = f"""search publications
              where year > 1999 and open_access = "{o}" and  category_for.id = {c}
              and type = "article" and research_orgs = "grid.6572.6"
              return year aggregate
                            count, rcr_avg, fcr_gavg,
                            citations_total, citations_median, citations_avg, recent_citations_total,
                            altmetric_median, altmetric_avg
              limit 50"""
      print("****************Loop:",o,c,"*****************************************")
      PubChunk = dsl.query(f"""{QUERY}""", verbose=False).as_dataframe()
   #####Create fields to indicate the search parameters that identified the included records:
      PubChunk['OpenAccess'] = o
      PubChunk['CAT_FOR_ID'] = c
      PubChunk['CAT_FOR'] = PubChunk['CAT_FOR_ID'].map(CF.set_index('id')['name'])
      print("Records in This Loop:           ",len(PubChunk))
      BigSet = pd.concat([BigSet, PubChunk])
      print("1 second pause for API Rest")
      time.sleep(1) # Seconds
      print("Running total records in BigSet:  ",len(BigSet))

BigSet = BigSet.rename({'id':'Year'}, axis=1)
BigSet.head(9)

#NOTE:  Be VERY careful about further summarizations of the data returned here.
# The counts represent all the publications that meet the crtieria of the loop.
# Publications generally have multiple authors, research_orgs, funders, categories, etc.
# and will be counted in multiple loops.

"""##Connect Cited and Citing Publications (ListChunk w/ SQL)"""

#   STEP 1:
##Find the id's of interesting publications:
CRBPubs = dsl.query_iterative(f"""search publications
                                  in title_abstract_only for "coral" or
                                  in title_abstract_only for "rabbitfish" or
                                  in title_abstract_only for "barnacle"
                                  where year = 1980
                                  return publications[id+year+times_cited]""", verbose=True).as_dataframe()
CRBPubs.head(4)
#Drop nulls to avoid errors:
RPs = CRBPubs['id'].dropna().tolist()
print(RPs)
print(len(RPs)," Records in RPs")

#CitedPubsList = ['pub.1015378969','pub.1063548752','pub.1011332010']
#   STEP 2:
#Pull information about publications that cited one or more of the publications identified above:
ChunkNumber = 1
#
# Find publications that cited any of the publications in the list above
q = """search publications
              where reference_ids in {} and year in [1986:2023]
              return publications[id+year+reference_ids]"""
#
results = []
for chunk in (list(chunks_of(list(RPs), 50))):
    print("Working on Chunk #",(ChunkNumber))
    ChunkNumber = ChunkNumber+1
    data = dsl.query_iterative(q.format(json.dumps(chunk)), verbose=False)
    results += data.publications
    time.sleep(1)
#
# put the data into a dataframe, remove duplicates
CitingPubs = pd.DataFrame().from_dict(results)
print("Publications found: ", len(CitingPubs))
CitingPubs.drop_duplicates(subset='id', inplace=True)
print("Unique publications found: ", len(CitingPubs))
CitingPubs.head(5)

CitingPub=CitingPubs.explode('reference_ids').reset_index()
CitingPub.head(9)


#Join and merge (can also do with Python Syntax)
#Summarize by Cited ID and Citing Publication Year
##!pip install pandasql
##from pandasql import sqldf
##import pandasql as ps


q = """
SELECT ed.id as citedid, ed.times_cited as TotalCitations, ed.year as PublicationYear,
      ing.id as citingid, ing.year as citation_year
  from CRBPubs ed
  left outer join CitingPub ing on ing.reference_ids = ed.id
  order by ed.id"""
JOINED = sqldf(q, globals())
print (len(JOINED),"Author/Publication/Most Relevant Concept Combinations")
JOINED.head(100)

q = """
SELECT ed.id as citedid, ed.year as PublicationYear, ing.year as citation_year,
      count(distinct(ing.id)) as CitationCount
  from CRBPubs ed
  left outer join CitingPub ing on ing.reference_ids = ed.id
  group by ed.id, ed.year, ing.year
  order by ed.id"""
JOINEDandGrouped = sqldf(q, globals())
print (len(JOINEDandGrouped),"Citations by Year")
JOINEDandGrouped.head(100)

"""##Prepare a Mini Data Warehouse to connect directly in PowerBI"""

##Instead of the "standard" connection information in the first cell in this "Starter Kit", use the following connection code:
##You will need to have a Python Environment set up on your machine and point PowerBI to that Environment.
##(If you've only used COLAB, this will be an extra step and it can be a little tricky)
##https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-python-scripts

##The below will result in a "mini warehouse" of tables that can be refreshed with one-click in PowerBI.
##Design the calls with the keys and detail you need to make the joins or lookups in PowerBI or Pandas as you see fit
##This method is likely preferable to a giant flat exploded table with lots of redundant data


##################Sample Code to embed Starts Here

import requests
import datetime
import dimcli
from dimcli.utils import *
import json
import sys
import pandas as pd
import numpy as np
                  #############Enter your key below
dimcli.login(key="YOUR KEY HERE",
             endpoint="https://app.dimensions.ai")
dimcli
dsl = dimcli.Dsl()

Authors = dsl.query_iterative("""search publications
                    where year in [2019:2022] and concepts = "octopus"
                    return publications[id+authors]""", verbose=True).as_dataframe_authors_affiliations()  ##researcher_id, pub_id, current_organization_ID

Pubs = dsl.query_iterative("""search publications
                    where year in [2019:2022] and concepts = "octopus"
                    return publications[id+title+year+times_cited+open_access+publisher+journal]""", verbose=True).as_dataframe()

RORGS = dsl.query_iterative("""search publications
                    where year in [2019:2022] and concepts = "octopus"
                    return publications[id+unnest(research_orgs)]""", verbose=True).as_dataframe()  ##research_orgs.id, research_orgs.name, research_orgs.types, research_orgs.county_name

Concepts = dsl.query_iterative("""search publications
                    where year in [2019:2022] and concepts = "octopus"
                    return publications[id+concepts_scores]""", verbose=True).as_dataframe_concepts()  ##research_orgs.id, research_orgs.name, research_orgs.types, research_orgs.county_name

SourceTitles = dsl.query("""search publications where concepts = "octopus"
                    return source_title limit 1000""", verbose=True).as_dataframe()  ##research_orgs.id, research_orgs.name, research_orgs.types, research_orgs.county_name

##################Code to embed ENDS Here

"""## Exporting Dataframes to GBQ Tables"""

### Applies to Dimensions on GBQ Customers only
### Use case - get the IDs of publications that meet full-text search criteria,
### Use the keyword to filter or group data in GBQ using SQL Syntax without record limits


#For Export to GBQ: (watch for permission prompt pop-up windows)
!pip install google-cloud-bigquery pandas
from google.colab import auth
auth.authenticate_user()
from google.cloud import bigquery

# Use API Calls and Python data manipulation to create your desired Dataframe:
OCTOPUS = %dsldf search publications for "octopus" where year = 2023 return publications[id] limit 100
OCTOPUS['Keyword'] = "Octopus"

MORAY = %dsldf search publications for "moray eel" where year = 2023 return publications[id] limit 100
MORAY['Keyword'] = "Moray Eel"

URCHIN = %dsldf search publications for "sea urchin" where year = 2023 return publications[id] limit 100
URCHIN['Keyword'] = "Sea Urchin"

#Manipulate as desired in Python and Pandas:
SeaCritters = pd.concat([OCTOPUS, MORAY, URCHIN])


#EXPORT TO GBQ

# Replace 'project_id' with your Google Cloud project ID
project_id = 'YOUR PROJECT ID HERE'
dataset_id = 'YOUR DATASET NAME HERE'
table_id = 'YOUR TABLE NAME HERE'  #in this example, SeaCritters
DF_To_Export = SeaCritters

# Initialize the BigQuery client
client = bigquery.Client(project=project_id)

# Define the dataset reference and table reference
dataset_ref = client.dataset(dataset_id)
table_ref = dataset_ref.table(table_id)

# Convert the DataFrame to a BigQuery-compatible format
job_config = bigquery.LoadJobConfig()
job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE #TRUNCATE overwrites the table if it exists

job = client.load_table_from_dataframe(DF_To_Export, table_ref, job_config=job_config)

# Wait for the job to complete
job.result()

print(f'Dataframe successfully written to BigQuery table: {project_id}.{dataset_id}.{table_id}')