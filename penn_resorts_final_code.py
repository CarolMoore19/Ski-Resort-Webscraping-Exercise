#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

#Resources:
#"Pennsylvania Snow Report," On the Snow (website)
#    https://www.onthesnow.com/pennsylvania/skireport.html
#Various resort web pages, On the Snow (website)
#"Implementing Web Scraping in Python with BeautifulSoup" Geeks for Geeks, Last Updated 20 Aug, 2020
#    https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/
#"Removing Numbers from a String", Stack Overflow,
#    https://stackoverflow.com/questions/12851791/removing-numbers-from-string"
#"Beautiful Soup Documentation," Crummy.Com
#    https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html?highlight=row
#Pandas Number Of Rows – 6 Methods, Data Independent, 14 Sept. 2020, 
#    https://www.dataindependent.com/pandas/pandas-number-of-rows/
#Pandas Documentation, “pandas.DataFrame.drop”, documentation.  
#    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop.html#pandas-dataframe-drop


import requests 
from bs4 import BeautifulSoup 
import csv 

#Read in URLs of ski resort data pages, eliminating '\n' 
filein=open("resorts.txt",'r')
urllist=[]
for i in filein:
    content = i.rstrip()
    urllist.append(content)

#This list shows keys for which a '%' sign will be added to the key name.
percent_metric=['BeginnerRuns','IntermediateRuns','AdvancedRuns','ExpertRuns']

#Create a list of dictionaries by iterating over all of the web pages
resortlist=[]

for url in urllist[:-1]:  #exclude last element of list which is an empty string.
    try:
        
        #Apply Beautiful Soup to of page with resort terrain stats
        r = requests.get(url) 
        soup = BeautifulSoup(r.content, 'html5lib') 
        terrain = soup.find('div', attrs = {'id':'resort_terrain'})  
 
        #Extract resort name out of URL and initiate dict
        name=url[0:-16]
        name=name[39:]
        terraindict={'Name':name} 
        
 
        #iterate over Beautiful Soup object
        for info in terrain.find("class"=="label"):
            
            #Remove numeric text to form keys
            elem=''.join((filter(str.isalpha, info.text)))
            
            #Add % sign to label if necessary
            if elem in percent_metric:
                elem=elem+"%"  
            
            #Use numerics for values and keep decimal point for Longest Run
            terraindict[elem]=''.join((filter(str.isdigit, info.text)))

        resortlist.append(terraindict)
        
    except:
        print("Possible error in ", url)
        
print(resortlist)

#Write list of dictionaries to CSV file using 'csv' module
filename = 'pennresorts2.csv'
with open(filename, 'w') as f: 
    w = csv.DictWriter(f,['Name','BeginnerRuns%','IntermediateRuns%','AdvancedRuns%',
                          'ExpertRuns%', 'Runs',"TerrainParks","NightSkiingac",
                          "LongestRunmi","SkiableTerrainac","SnowMakingac"]) 
    w.writeheader() 
    for data in resortlist: 
        w.writerow(data) 


#Read data into pandas for analysis
import pandas as pd
df = pd.read_csv('pennresorts2.csv') 

#I was not able to scrape accurate data for this field.
del df['LongestRunmi'] 

#Additional data validation
origrows = len(df.axes[0]) #number of original rows 

#Drop obs if percentages add to more than 103 or less than 97
df['percsum'] = df['BeginnerRuns%']+df['IntermediateRuns%']+df['AdvancedRuns%']\
    +df['ExpertRuns%']
df = df.drop(df[df['percsum']>103].index) 
df = df.drop(df[df['percsum']<97].index)  

#Drop obs if percent > 90 in any category
df = df.drop(df[df['BeginnerRuns%']>90].index)  
df = df.drop(df[df['IntermediateRuns%']>90].index)  
df = df.drop(df[df['AdvancedRuns%']>90].index)  
df = df.drop(df[df['ExpertRuns%']>90].index)  
newrows2=len(df.axes[0])
print("The original num obs was: ", origrows,"The new num obs is: ",newrows2)

#Report average percentage of runs in each ability level
def runavgs(df): 
    
    print("The average percentage of beginner runs is:",round(df['BeginnerRuns%'].mean(),2))
    print("The average percentage of intermediate runs is:",round(df['IntermediateRuns%'].mean(),2))
    print("The average percentage of advanced runs is:",round(df['AdvancedRuns%'].mean(),2))
    print("The average percentage of expert runs is:",round(df['ExpertRuns%'].mean(),2))
    
runavgs(df)  

#Classify resorts
def most_terrainparks(df):
    df['max_parks']=df['TerrainParks'].max()
    datamax=df[(df['TerrainParks'] == df['max_parks'])]
    print("Most terrain parks: ", datamax['Name'])
    print("Number of parks:  ",datamax['max_parks'].max())
    df.sort_values(by=['TerrainParks'], inplace=True, ascending=False)
    print(df[['Name',"TerrainParks"]])
most_terrainparks(df)

def beginner_friendly(df):
    df['num_beginner_runs'] = round(df['BeginnerRuns%']*df['Runs']/100,0)
    
    df['max_green']=df['num_beginner_runs'].max()
    datagreens=df[(df['num_beginner_runs'] == df['max_green'])]
    print("Most beginner friendly: ", datagreens['Name'])
    print("Number of beginner runs:  ",datagreens['max_green'].max())
    df.sort_values(by=['num_beginner_runs'], inplace=True, ascending=False)
    print(df[['Name','BeginnerRuns%','Runs','num_beginner_runs']])

    
beginner_friendly(df)