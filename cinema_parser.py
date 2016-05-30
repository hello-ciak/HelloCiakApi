import requests
from bs4 import BeautifulSoup

CACHE_KEY_SEPARATOR = '_'
GOOGLE_CACHE_KEY = 'google_movies_response'
API_ENDPOINT = 'https://www.google.com/movies'


class CinemaParser:
    def __init__(self, near, app, cache):
        self.near = near
        self.app = app
        self.cache = cache

    def get(self, cinema_name=None, movie_name=None):
        self.app.logger.debug('Incoming request, "near": "%s", "cinema_name": "%s", "movie_name": "%s"' % (self.near,
                                                                                                           cinema_name,
                                                                                                           movie_name))

        # calculate the key to use in Redis
        cache_key = CACHE_KEY_SEPARATOR.join([GOOGLE_CACHE_KEY,
                                              str(self.near),
                                              str(cinema_name),
                                              str(movie_name)])

        if self.cache.has(cache_key):
            self.app.logger.debug('serving "%s" key from cache' % cache_key)
            cached_request_content = self.cache.get(cache_key)

            # parse response from cached result
            parser = BeautifulSoup(cached_request_content, 'html.parser')
        else:
            # response not found in cache, ask Google
            self.app.logger.debug('key "%s" was not found in redis cache, asking Google...' % cache_key)
            request = requests.get(API_ENDPOINT, params={'near': self.near})
            parser = BeautifulSoup(request.content, 'html.parser')

            # set Google call in cache
            self.cache.set(cache_key, request.content)

        # this will be the final output that will be jsonized in API response
        output = []

        theaters = parser.select('.theater')

        for theater in theaters:
            theater_name = theater.find('h2').text

            if cinema_name is not None and theater_name.lower() != cinema_name.strip().lower():
                continue

            theater_infos = {
                'theater_name': theater_name,
                'theater_info': theater.find('div', {'class': 'info'}).text,
                'movies': []
            }

            movies = theater.find_all('div', {'class': 'movie'})

            for movie in movies:
                title = movie.find('a').text

                if movie_name is not None and movie_name.strip().lower() != title.lower():
                    continue

                times = movie.find('div', {'class': 'times'}).find_all('span')
                times_strings = []
                movie_info = movie.find('span', {'class': 'info'}).text

                # concat all the movie timings
                for time in times:
                    time_text = time.text.strip()

                    if time_text:
                        times_strings.append(time_text)

                theater_infos['movies'].append({
                    'title': title,
                    'times': ' - '.join(times_strings),
                    'movie_info': movie_info
                })

            # return the theater infos only if some movies are there
            if theater_infos['movies']:
                # append all the theater infos
                output.append(theater_infos)

        # return JSON output
        return {'data': output}
