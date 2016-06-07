import os
from os.path import join, dirname
from urllib.parse import urlparse

import flask
from dotenv import load_dotenv
from flask import Flask, request
from sqlalchemy import Table, Column, Sequence, Integer, String, MetaData
from sqlalchemy import create_engine
from werkzeug.contrib.cache import RedisCache

from cinema_parser import CinemaParser

# load dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# initialise Flask app
app = Flask(__name__)
app.debug = bool(int(os.environ.get('DEBUG')))

# parse the Redis url (coming from Heroku or .env)
redis_url = urlparse(os.environ.get('REDIS_URL'))

# initialise Redis caching engine
redis_cache = RedisCache(port=redis_url.port,
                         host=redis_url.hostname,
                         password=redis_url.password)

##########################
# create database engine #
##########################
engine = create_engine(os.environ.get('DATABASE_URL'))

metadata = MetaData()

# table definition
locations_table = Table('locations', metadata,
                        Column('id', Integer, Sequence('location_id_seq'), primary_key=True),
                        Column('location', String, nullable=False))

# create locations table (it checks table existence, so it's
# safe to call multiple times)
metadata.create_all(engine)


@app.route('/')
def api():
    near = request.args.get('near')
    cinema_name = request.args.get('cinema_name')
    movie_name = request.args.get('movie_name')

    insert = locations_table.insert().values(location=str(near).strip())

    engine.connect()
    engine.execute(insert)

    # Redis cache is injected as service in constructor
    parser = CinemaParser(near, app=app, cache=redis_cache)

    return flask.jsonify(parser.get(cinema_name=cinema_name, movie_name=movie_name))


@app.route('/locations')
def locations():
    grouped_locations = engine.execute(
        """
        SELECT location, count(*) FROM locations GROUP BY location
        """).fetchall()

    return flask.jsonify(grouped_locations)


if __name__ == '__main__':
    api_port = int(os.environ.get('PORT'))
    api_host = os.environ.get('API_HOST')

    app.run(host=api_host, port=int(api_port))
