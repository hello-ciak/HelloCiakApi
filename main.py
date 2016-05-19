import os

import flask
from flask import Flask, request
from cinema_parser import CinemaParser

app = Flask(__name__)
app.debug = True


@app.route('/')
def api():
    near = request.args.get('near')
    cinema_name = request.args.get('cinema_name')
    movie_name = request.args.get('movie_name')

    parser = CinemaParser(near)

    # return flask.jsonify(parser.get(cinema_name='Multisala Edera', movie_name='La pazza gioia'))
    return flask.jsonify(parser.get(cinema_name=cinema_name, movie_name=movie_name))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
