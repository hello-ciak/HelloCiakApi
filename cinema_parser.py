import requests
from bs4 import BeautifulSoup

API_ENDPOINT = 'https://www.google.com/movies'


class CinemaParser:
    def __init__(self, near):
        self.near = near

    def get(self, cinema_name=None, movie_name=None):
        request = requests.get(API_ENDPOINT, params={'near': self.near})
        parser = BeautifulSoup(request.content, 'html.parser')
        output = []

        theaters = parser.select('.theater')

        for theater in theaters:
            theater_name = theater.find('h2').find('a').text

            if cinema_name is not None and theater_name.lower() != cinema_name.lower():
                continue

            theater_infos = {
                'theater_name': theater_name,
                'theater_info': theater.find('div', {'class': 'info'}).text,
                'movies': []
            }

            movies = theater.find_all('div', {'class': 'movie'})

            for movie in movies:
                title = movie.find('a').text

                if movie_name is not None and movie_name.lower() != title.lower():
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

            # append all the theater infos
            output.append(theater_infos)

        # return JSON output
        return {'data': output}
