import numpy as np
from datetime import datetime
from fancygradient import get_colors


# if True then use the global data, if False then use the US data

# global/US, region label, population (can be None), country/state, area 

REGIONS = [
    (True, 'US', 327.2, 'US', ''),
    (True, 'China', 58.5, 'China', ''),
    (True, 'Spain', 47.7, 'Spain', ''),
    (True, 'Italy', 60.5, 'Italy', ''),
    (True, 'Japan', 126.8, 'Japan', ''),
    (True, 'S Korea', 51.5, 'Korea, South', ''),
    (True, 'UK', 66.4, 'United Kingdom', ''),
    (True, 'Germany', 82.8, 'Germany', ''),
    (False, 'New York', 19.2, 'New York', ''),
    (True, 'Sweden', 67.0, 'Sweden', ''),
    (True, 'Switzerland', 8.6, 'Switzerland', ''),
    (False, 'New York City', 8.6, 'New York', 'New York'),
    (True, 'Russia', 144.5, 'Russia', ''),
]


DAYS_TOTAL = 128
CASES_DATA_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
DEATH_DATA_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
CASES_FILENAME = 'cases.csv'
DEATHS_FILENAME = 'deaths.csv'

CASES_DATA_US_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
DEATH_DATA_US_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
CASES_US_FILENAME = 'cases_us.csv'
DEATHS_US_FILENAME = 'deaths_us.csv'

IMG_FILENAME = 'chart.png'
PROJ_VALS_FILENAME = 'projected_values.csv'

FIRST_STAMP = 1579651200  # 1.22.2020
FIRST_DAY_IDX = 14

FILTER_WIN_SIZE = 17

# used for curve fitting
MIN_PERIOD = 4 * 7
MAX_PERIOD = 8 * 7

# weighting coefficient; a larger value means the curve will be fitted to the latest values more tightly 
Qc = 1.6    # for the confirmed cases chart
Qd = 1.2    # for the deaths chart


COLORS = get_colors(('#ff0055', '#00ddff', '#ff9d00', '#18ed00', '#ff0055'))


DATES = []
TICKS = []


for i in range(1, DAYS_TOTAL):
    dt = datetime.utcfromtimestamp(FIRST_STAMP + i * 24 * 3600)
    DATES.append(dt.strftime('%b %d'))

    if dt.weekday() == 6 and i > FIRST_DAY_IDX:
        TICKS.append(i - 1)


def func_fit_exp(x, a, b, c, d):
    return b * (1 - a ** x)


def func_fit_lin(x, a, b, c, d):
    return a * x + b


def func_sigma(x, q):
    return q ** x
