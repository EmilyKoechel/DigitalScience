# -*- coding: utf-8 -*-
"""SimpleResearcherFinder.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14gOSGJ4mq2qtITdMEdqWI70j7z822PvJ
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
##Check for updated versions of the StarterKit: https://github.com/EmilyKoechel/DigitalScience

"""## Python Librarie and API Connection"""

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

#Connect to DimensionsAPI
from google.colab import drive
drive.mount('/content/drive')
file_path = "/content/drive/My Drive/APIKeys.csv" #Be sure this location is ONLY accessible by you.
df = pd.read_csv(file_path)
MY_KEY = df.at[0, 'DimensionsKey']
dimcli.login(key=MY_KEY, endpoint="https://app.dimensions.ai")

##Alternatively, type your key into the space below between double quotes:
##Please do not share code containing your Key as your Key is specific to you
##dimcli.login(key="YOUR KEY HERE", endpoint="https://app.dimensions.ai")

"""##People ID Finder - Name, Department, Institution"""

##In Excel or GoogleSheets, create a worksheet with columns for Identifier (optional), FirstName, LastName, Department (or Keyword), Institution
##Blanks or Null values will cause an error. Be sure every cell is populated
##Save As Tab Delimited
#Read the file into a PANDAS Dataframe:
from google.colab import drive
drive.mount('/content/drive')
file_path = "/content/drive/My Drive/ColabConnect/Faculty.tsv"  ##Adjust path and filename as needed
Faculty = pd.read_csv(file_path, sep='\t', encoding='utf-8')
Faculty.head(9)

dsl = dimcli.Dsl()
INPUTS = Faculty
#INPUTS = Faculty.head(8)  #This line for testing only - comment out for full run

Results = pd.DataFrame()
INPUTSRecCount= len(INPUTS)
RunTime = "{:.2f}".format(INPUTSRecCount * 5 / 60)
LoopNo = 0
print("This should take approximately ",RunTime," minutes to complete.")

query_template = """
search publications
for "{}"
where authors = "{}" and authors = "{}"
and research_org_names = "{}"
return researchers[id+first_name+last_name+orcid_id+obsolete]
limit 10"""

for index, row in INPUTS.iterrows():
    Department = row['Department']
    FirstName = row['FirstName']
    LastName = row['LastName']
    Institution = row['Institution']
    Name = row['Name']
    LoopNo = (LoopNo + 1)
    data = pd.DataFrame()
    print("*****Loop ",LoopNo," of ", Name, Department, Institution, "***************************************")
    try:
        q = query_template.format(Department,FirstName,LastName,Institution)
        #print(q)
        data = dsl.query(q).as_dataframe()
        data['InputName'] = Name
        data['Department'] = Department
        data['Institution'] = Institution
    except Exception as e:
        # Handle the error by creating the 'data' DataFrame with the 'Reject_ManID' and error flag
        data = pd.DataFrame({'Name': [Name], 'id': ['error']})
    Results = pd.concat([Results, data])
    time.sleep(.33)  # Seconds
Results.head(200)

#Ideally, the top researcher ID for each name will be the correct one
#However, sometimes we won't find a match or the match will be farther down or we will find more than one match.
#Here we compare the searched names to the found names to find the best fit and idenfify non-matches:
!pip install fuzzywuzzy[speedup]
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
#https://pypi.org/project/fuzzywuzzy/

SuperSet = Results
SuperSet['DimName'] = SuperSet['last_name']+', '+SuperSet['first_name']
SuperSet['NameRatio'] = SuperSet.dropna(subset=['InputName', 'DimName']).apply(lambda x: fuzz.ratio(x.InputName, x.DimName), axis=1)
#SuperSet = SuperSet.sort_values(['InputName','NameRatio'],ascending=[True,False])
SuperSet['RIDLink'] =  'https://app.dimensions.ai/discover/publication?search_mode=content&and_facet_researcher='+SuperSet['id']
SuperSet['Index_no'] = SuperSet.groupby(['InputName']).cumcount()+1;

SuperSet = SuperSet[(SuperSet['Index_no'] == 1) | (SuperSet['NameRatio'] >= 70)]
condition = SuperSet['NameRatio'] < 75
SuperSet.loc[condition, ['id', 'first_name', 'last_name', 'count', 'obsolete', 'orcid_id','DimName','RIDLink']] = '<ERROR!>'


print(len(INPUTS))
print(len(SuperSet))
SuperSet.head(200)

"""##Nobel Prize List (an example of how to edit to fit the data you have)"""

#Upload Interesting Names:
from google.colab import files
uploaded = files.upload()
#You will be prompted to browse to a file.  Put the file name below:
import io
Faculty = pd.read_csv(io.BytesIO(uploaded[r'NobelWinners.csv']),encoding='latin1')
Faculty = Faculty[['awardYear','category','id','givenName','familyName','fullName','gender','affiliation_1','affiliation_2','affiliation_3','affiliation_4']]
Faculty['affiliation_1'] = Faculty['affiliation_1'].str.split(',', 1).str[0]
Faculty['affiliation_1'].fillna("university", inplace=True)


Faculty.head(20)

dsl = dimcli.Dsl()
INPUTS = Faculty
#INPUTS = Faculty.head(8)  #This line for testing only - comment out for full run

Results = pd.DataFrame()
INPUTSRecCount= len(INPUTS)
RunTime = "{:.2f}".format(INPUTSRecCount * 5 / 60)
LoopNo = 0
print("This should take approximately ",RunTime," minutes to complete.")


#Adjust the query to fit the data that you have available:
query_template = """
search publications
for "{}"
where authors = "{}" and authors = "{}"
and research_org_names = "{}"
and year <= {}
return researchers[id+first_name+last_name+orcid_id+obsolete]
limit 10"""

for index, row in INPUTS.iterrows():
    Department = row['category']
    FirstName = row['givenName']
    LastName = row['familyName']
    year = row['awardYear']
    Institution = dsl_escape(row['affiliation_1'], True)
    Name = row['fullName']
    LoopNo = (LoopNo + 1)
    data = pd.DataFrame()
    print("*****Loop ",LoopNo," of ", Name, Department, Institution, "***************************************")
    try:
        q = query_template.format(Department,FirstName,LastName,Institution,year)
        #q = query_template.format(Department,FirstName,LastName,year)
        #print(q)
        data = dsl.query(q).as_dataframe()
        data['InputName'] = Name
        data['Category'] = Department
        data['affiliation'] = Institution

    except Exception as e:
        # Handle the error by creating the 'data' DataFrame with the 'Reject_ManID' and error flag
        data = pd.DataFrame({'fullName': [Name], 'id': ['error']})
    Results = pd.concat([Results, data])
    time.sleep(.33)  # Seconds
Results.head(200)



#Ideally, the top researcher ID for each name will be the correct one
#However, sometimes we won't find a match or the match will be farther down or we will find more than one match.
#Here we compare the searched names to the found names to find the best fit:
!pip install fuzzywuzzy[speedup]
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
#https://pypi.org/project/fuzzywuzzy/

SuperSet = Results
SuperSet['DimName'] = SuperSet['last_name']+', '+SuperSet['first_name']
SuperSet['NameRatio'] = SuperSet.dropna(subset=['InputName', 'DimName']).apply(lambda x: fuzz.ratio(x.InputName, x.DimName), axis=1)
#SuperSet = SuperSet.sort_values(['InputName','NameRatio'],ascending=[True,False])
SuperSet['RIDLink'] =  'https://app.dimensions.ai/discover/publication?search_mode=content&and_facet_researcher='+SuperSet['id']
SuperSet['Index_no'] = SuperSet.groupby(['InputName']).cumcount()+1;

SuperSet = SuperSet[(SuperSet['Index_no'] == 1) | (SuperSet['NameRatio'] >= 70)]
condition = SuperSet['NameRatio'] < 75
SuperSet.loc[condition, ['id', 'first_name', 'last_name', 'count', 'obsolete', 'orcid_id','DimName','RIDLink']] = '<ERROR!>'


print(len(INPUTS))
print(len(SuperSet))
SuperSet.head(200)