import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import matplotlib.pyplot as plt
import re

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


#return a list of tuples in the format (year,title) for first ten movies of that year

def getMovieNames(year):
    url = 'https://filmsite.org/' + str(year) + ".html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    anchor = soup.find_all('p')
    x = []
    reg = r'\b(.+)\('
    for i in anchor:
        try:
            orig = i.find('b').text
        except:
            continue
        y = re.findall(reg, orig)
        for j in y:
            x.append(j[:-1])
    new_lst = x[1:11]
    tuple_lst = []
    for i in new_lst:
        tuple_lst.append((year, i))

    return tuple_lst


#call getMovieNames for each year dating back to 1919 to add all of the movie titles and years to the table movies

def moviesToDatabase(url):
    pass


print(getMovieNames(2020))