import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import matplotlib.pyplot as plt
import re
import json

apikey = "03e0285dfamshd7009361d489213p1ccea2jsn9774610651db"

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
    reg = r'\b([a-zA-Z0-9\'\, ]+)\('
    for i in anchor:
        try:
            orig = i.find('b').text
        except:
            continue
            try:
                orig = i.find('a').text
            except:
                continue
        y = re.findall(reg, orig)
        for j in y:
            x.append(j[:-1])
    tuple_lst = []
    for i in x:
        tuple_lst.append((year, i))

    return tuple_lst


def getMovieID(title, year):
    url = "https://movies-tvshows-data-imdb.p.rapidapi.com/"

    querystring = {"type":"get-movies-by-title","title": str(title)}

    headers = {
        'x-rapidapi-key': apikey,
        'x-rapidapi-host': "movies-tvshows-data-imdb.p.rapidapi.com"
    }
    try:

        response = requests.request("GET", url, headers=headers, params=querystring)
        results = json.loads(response.text)['movie_results']
        key = ''
        for i in results:
            if i['year'] == year and i['title'] == title:
                key = i['imdb_id']

        return key
    except:
        return "ignore"


def getMovieData(imdb_id):
    url = "https://movies-tvshows-data-imdb.p.rapidapi.com/"

    querystring = {"type":"get-movie-details","imdb": str(imdb_id)}

    headers = {
        'x-rapidapi-key': apikey,
        'x-rapidapi-host': "movies-tvshows-data-imdb.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    results = json.loads(response.text)
    year = int(results['year'])
    title = results['title']
    genre = results['genres'][0]
    rating = float(results['imdb_rating'])
    popularity = float(results['popularity'])

    return (imdb_id, year, title, genre, rating, popularity)





#call getMovieNames for each year dating back to 1919 to add all of the movie titles, years, genres, ratings, and popularity to the table movies

def createMoviesTable(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Movies")
    cur.execute("CREATE TABLE Movies (imdb_id TEXT PRIMARY KEY, year INTEGER, title TEXT, genre TEXT, rating REAL, popularity REAL)")
    for i in range(20):
        year = 2000 + i
        names = getMovieNames(year)
        print(names)
        id_lst = []
        for k in names:
            if len(id_lst) < 10:
                if getMovieID(k[1], k[0]) != '' and getMovieID(k[1], k[0]) != "ignore":
                    id_lst.append(getMovieID(k[1], k[0]))
        print(id_lst)
        for j in id_lst:
            data = getMovieData(j)
            cur.execute("INSERT INTO Movies (imdb_id,year,title,genre,rating,popularity) VALUES (?,?,?,?,?,?)", data)
            conn.commit()
    pass


cur, conn = setUpDatabase('movie_database.db')
createMoviesTable(cur, conn)