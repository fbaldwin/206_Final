import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import matplotlib.pyplot as plt

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


#return a list of tuples in the format (year,title) for first ten movies of that year

def getMovieNames(year):
    url = 'filmsite.org/' + str(year) + ".html"
    r = requests.get(url)

    pass


#call getMovieNames for each year dating back to 1919 to add all of the movie titles and years to the table movies

def moviesToDatabase(url):
    pass