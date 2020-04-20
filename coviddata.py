import numpy as np
import requests
import csv

from constants import *


def _download(url, filename):
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)


def get_global_data(country, state='', category='cases', download=False):

    resources = {
        'cases': (CASES_DATA_URL, CASES_FILENAME),
        'deaths': (DEATH_DATA_URL, DEATHS_FILENAME)
    }

    if not category in resources:
        return []

    def _data(row):
        return np.array(list(map(lambda x: int(x), row[4:])))

    try:
        url, filename = resources[category]

        if download:
            _download(url, filename)

        with open(filename, newline='') as csvfile:
            data = np.array([])
            reader = csv.reader(csvfile)
            # dates = next(reader)[4:]

            for row in reader:
                _state = row[0]
                _country = row[1]

                if state:
                    if _country == country and _state == state:
                        return _data(row)
                else:
                    if _country == country:
                        data = data + _data(row) if data.size else _data(row)

            return data

    except Exception as e:
        print(e)
        return []


def get_us_data(state, city='', category='cases', download=False):

    resources = {
        'cases': (CASES_DATA_US_URL, CASES_US_FILENAME), 
        'deaths': (DEATH_DATA_US_URL, DEATHS_US_FILENAME)
    }

    if not category in resources:
        return []

    def _data(row):
        return np.array(list(map(lambda x: int(x), row[12:])))

    try:
        url, filename = resources[category]

        if download:
            _download(url, filename)

        with open(filename, newline='') as csvfile:
            data = np.array([])
            reader = csv.reader(csvfile)

            for row in reader:
                _admin2 = row[5]
                _state = row[6]

                if city:
                    if _state == state and _admin2 == city:
                        return _data(row)
                else:
                    if _state == state:
                        data = data + _data(row) if data.size else _data(row)

            return data

    except Exception as e:
        print(e)
        return []


def download():
    for resources in (
        (CASES_DATA_URL, CASES_FILENAME), 
        (DEATH_DATA_URL, DEATHS_FILENAME), 
        (CASES_DATA_US_URL, CASES_US_FILENAME), 
        (DEATH_DATA_US_URL, DEATHS_US_FILENAME)
    ):
        try:
            _download(*resources)
            print('>> downloaded')
        except Exception as e:
            print(e)
