import os
from os.path import join, dirname
from urllib.parse import urlparse

import flask
from dotenv import load_dotenv
from flask import Flask, request
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


@app.route('/')
def api():
    near = request.args.get('near')
    cinema_name = request.args.get('cinema_name')
    movie_name = request.args.get('movie_name')

    # Redis cache is injected as service in constructor
    parser = CinemaParser(near, cache=redis_cache)

    return flask.jsonify(parser.get(cinema_name=cinema_name, movie_name=movie_name))


if __name__ == '__main__':
    api_port = int(os.environ.get('PORT'))
    api_host = os.environ.get('API_HOST')

    app.run(host=api_host, port=int(api_port))
