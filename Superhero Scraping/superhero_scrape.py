# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 18:31:01 2019

@author: Max Tchibozo
"""


import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

URL = "https://en.wikipedia.org/wiki/List_of_films_based_on_Marvel_Comics_publications"

res = requests.get(URL).text
soup = BeautifulSoup(res,'lxml')
links={}
for items in soup.find('table', class_='wikitable sortable').find_all('i'):
    links[items.a.text]="https://en.wikipedia.org"+items.a['href']
    

URL1 =  "https://en.wikipedia.org/wiki/List_of_films_based_on_DC_Comics_publications"

res1 = requests.get(URL1).text
soup1 = BeautifulSoup(res1,'lxml')

for items in soup1.find('table', class_='wikitable sortable').find_all('tr'):
    if len(items.find_all('i')) != 0:
        links[items.find_all('i')[0].text]= "https://en.wikipedia.org"+items.find_all('i')[0].a['href']
fin_dict={}

for i in links:
    fin_dict[i]={}

for j in links:
    res1 = requests.get(links[j]).text
    soup1 = BeautifulSoup(res1,'lxml')
    for items in soup1.find_all('a'):
        if items.has_attr('href'):
            if items['href'].startswith("https://www.rottentomatoes.com/m/"):
                fin_dict[j]['rt']=items['href']
            if re.match("^https://www.imdb.com/title/tt[^/]+/$",items['href'])!=None:
                fin_dict[j]['imdb']=items['href']
            if items['href'].startswith("https://www.boxofficemojo.com/movies/?id="):
                fin_dict[j]['bm']=items['href']



rt_count = 0
imdb_count = 0
bm_count = 0

print("nb movies : "+str(len(fin_dict)))


for i in fin_dict.keys():
    if "rt" in fin_dict[i].keys():
        rt_count += 1
    if "imdb" in fin_dict[i].keys():
        imdb_count += 1
    if "bm" in fin_dict[i].keys():
        bm_count += 1

print("rt : "+str(rt_count))
print("imdb : "+str(imdb_count))
print("bm : "+str(bm_count))

#We have all movie pages from imdb
for movie in fin_dict.keys():
    
    #We first scrape the data from imdb
    url_imdb = fin_dict[movie]['imdb']
    res = requests.get(url_imdb).text
    soup = BeautifulSoup(res,'lxml')
    
    try:
        #Extracting rating (IMDB user rating)
        imdb_rating = soup.find("div","ratingValue").find(itemprop="ratingValue").text
        fin_dict[movie]["imdb_rating"] = imdb_rating
        print("imdb rating : ",imdb_rating)
    except: #movie has no rating
        print(movie)
    
    try:
        tmp = soup.findAll("div","txt-block")
        for k in range(len(tmp)):
    
        #Extracting Release Date
            if "Release Date:" in tmp[k].select("h4")[0].text:
                release_date = str(tmp[k]).split("Release Date:</h4>")[1].split("\n")[0]
                fin_dict[movie]["release_date"] = release_date
                print("Release Date:",release_date)
    
        #Extracting budget        
            if "Budget:" in tmp[k].select("h4")[0].text:
                budget = str(tmp[k]).split("Budget:</h4>")[1].split(" ")[0][:-1]
                fin_dict[movie]["budget"] = budget
                print("Budget : ",budget)
                
        #Extracting Opening weekend USA    
            if "Opening Weekend USA:" in tmp[k].select("h4")[0].text:
                opening_weekend_usa = str(tmp[k]).split("Opening Weekend USA:</h4>")[1].split("\n")[0][:-1]
                fin_dict[movie]["opening_weekend_usa"] = opening_weekend_usa
                print("Opening Weekend USA:",opening_weekend_usa)
                
        #Extracting Domestic Gross
            if "Gross USA:" in tmp[k].select("h4")[0].text:
                gross_usa = str(tmp[k]).split("Gross USA:</h4>")[1].split(" ")[1]
                fin_dict[movie]["gross_usa"] = gross_usa
                print("Gross USA:",gross_usa)
        
        #Extracting Worldwide Gross
            if "Cumulative Worldwide Gross:" in tmp[k].select("h4")[0].text:
                gross_worldwide = str(tmp[k]).split("Cumulative Worldwide Gross:</h4>")[1].split(" ")[1]
                fin_dict[movie]["gross_worldwide"] = gross_worldwide 
                print("Gross worldwide:",gross_worldwide)
    except: #when we have passed the k which contained the above info
        pass
            
    #We then scrape the critic score and audience score from rotten tomatoes
    if "rt" in fin_dict[movie].keys():
        url_rt = fin_dict[movie]['rt']
        res = requests.get(url_rt).text
        soup = BeautifulSoup(res,'lxml')
        try:
            #Extracting critic score from RT
            for item in soup.find("span","mop-ratings-wrap__percentage").text.split(" "):
                if "%" in str(item):
                    critic_score_rt = str(item)[:-1]
                    fin_dict[movie]["critic_score_rt"] = critic_score_rt
                    print("Critic score RT: ",critic_score_rt)
            
            for item in soup.findAll("span","mop-ratings-wrap__percentage")[1].text.split(" "):
                if "%" in str(item):
                    audience_score_rt = str(item)[:-1]
                    fin_dict[movie]["audience_score_rt"] = audience_score_rt
                    print("Audience score RT : ",audience_score_rt)
            
        except:
            pass
    
    if "bm" in fin_dict[movie].keys():
        url_bm = fin_dict[movie]["bm"]
        res = requests.get(url_rt).text
        soup = BeautifulSoup(res,'lxml')    
    #We then scrape the number of theaters from box office mojo
    #TODO
    
    
def string_to_float(value):
    if type(value) == str:
        new_value = value.replace(",","")
        new_value = new_value.replace("$","")
        new_value = float(new_value)
        return new_value
    else: #value is an NA
        return value

            
    

df = pd.DataFrame.from_dict(fin_dict, orient='index')
df['budget'] = df['budget'].apply(lambda x: string_to_float(x))
df['opening_weekend_usa'] = df['opening_weekend_usa'].apply(lambda x: string_to_float(x))
df['gross_usa'] = df['gross_usa'].apply(lambda x: string_to_float(x))
df['gross_worldwide'] = df['gross_worldwide'].apply(lambda x: string_to_float(x))

df.to_csv('superhero_movie_dataframe.csv')




"""
Critic score (RT - DONE)
Audience score (imdb - DONE)
Revenue (imdb - DONE)
Budget (imdb - DONE)
Year produced/released (imdb - DONE)
Number of theaters allocated for the first week after release
Domestic gross (imdb - DONE)
Worldwide gross (imdb - DONE)
Revenue in first weekend (imdb - DONE)
"""