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
    reg = r'\b([a-zA-Z0-9\'\,\.\&\:\-éá\/\! ]+)\('
    for i in anchor:
        try:
            orig = i.find('b').text
        except:
            try:
                orig = i.find('a').text
            except:
                try:
                    orig = i.find('strong').text
                except:
                    continue
        y = re.findall(reg, orig)
        for j in y:
            st = j[:-1].strip()
            x.append(st)
    tuple_lst = []
    for i in x:
        tuple_lst.append((year, i))

    return tuple_lst


def createMoviesTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Movies (year INTEGER, title TEXT)")
    for i in range(21):
        year = 2000 + i
        names = getMovieNames(year)
        for j in range(len(names)):
            print(names[j])
            cur.execute("INSERT INTO Movies (year, title) VALUES (?,?)", (names[j][0], names[j][1]))
    conn.commit()
    pass


def createIDTable(cur, conn):
    cur.execute("DROP TABLE IF EXISTS IDs")
    cur.execute("CREATE TABLE IF NOT EXISTS IDs (imdb_id TEXT PRIMARY KEY, title TEXT)")
    years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    for k in years:
        cur.execute("SELECT year, title FROM Movies WHERE year = ?", (k,))
        movs = cur.fetchall()
        print(movs)
        id_lst = []
        for i in movs:
            year = i[0]
            title = i[1]
            imdb_id = getMovieID(title, year)
            if len(id_lst) < 10:
                if imdb_id != '' and imdb_id != "ignore":
                    id_lst.append(imdb_id)
                    print('adding ' + str(title))
                    cur.execute("INSERT INTO IDs (imdb_id, title) VALUES (?,?)", (imdb_id, title))
                else:
                    print('Could not find ID for ' + str(title))
    conn.commit()
    
    pass

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
    genre = results['genres'][0]
    rating = float(results['imdb_rating'])
    popularity = float(results['popularity'])

    return (imdb_id, genre, rating, popularity)





#call getMovieNames for each year dating back to 1919 to add all of the movie titles, years, genres, ratings, and popularity to the table movies

def createRatingsTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Ratings (imdb_id TEXT PRIMARY KEY, genre TEXT, rating REAL, popularity REAL)")
    cur.execute("SELECT imdb_id FROM IDs")
    ids = cur.fetchall()
    print(ids)
    for i in ids:
        data = getMovieData(i[0])
        cur.execute("INSERT INTO Ratings (imdb_id,genre,rating,popularity) VALUES (?,?,?,?)", data)
    conn.commit()
    pass


def getAverageRating(year, cur, conn):
    cur.execute("SELECT IDs.imdb_id FROM IDs JOIN Movies ON IDs.title = Movies.title WHERE year = ?", (year,))
    ids = cur.fetchall()
    ratings = []
    total = 0
    for i in ids:
        cur.execute("SELECT rating FROM Ratings WHERE imdb_id = ?", (i[0],))
        rate = cur.fetchone()
        total += rate[0]
        ratings.append(rate[0])
    average = total / len(ratings)
    return average


def getAveragePopularity(year, cur, conn):
    cur.execute("SELECT IDs.imdb_id FROM IDs JOIN Movies ON IDs.title = Movies.title WHERE year = ?", (year,))
    ids = cur.fetchall()
    ratings = []
    total = 0
    for i in ids:
        cur.execute("SELECT popularity FROM Ratings WHERE imdb_id = ?", (i[0],))
        rate = cur.fetchone()
        total += rate[0]
        ratings.append(rate[0])
    average = total / len(ratings)
    return average

    


cur, conn = setUpDatabase('movie_database.db')
print(getAveragePopularity(2019, cur, conn))