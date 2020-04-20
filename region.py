import warnings
import math
from typing import NamedTuple

import numpy as np
from numpy import convolve
from scipy.optimize import curve_fit
from scipy.signal.windows import hann
import matplotlib.pyplot as plt

from constants import *


warnings.filterwarnings('ignore')


class FitErrOutput(NamedTuple):
    min_err: float
    idx: int
    period: int
    errors: tuple


class FitOutput(NamedTuple):
    current_actual: int = 0
    current: float = 0
    current_h: float = 0
    daily_inc: float = 0
    in_1wk: float = np.nan
    in_2wk: float = np.nan


class ProjectedValues(NamedTuple):
    current_actual: int = 0
    current: float = 0
    current_h: float = 0
    daily_inc: float = 0
    in_1wk: float = 0
    in_2wk: float = 0
    current_daily: float = 0
    in_1wk_daily: float = 0
    in_2wk_daily: float = 0
    err_1wk: float = np.nan
    err_2wk: float = np.nan


def _get_fit_errors(cases, f, q, min_period, max_period):

    # since the result of the curve fitting depends a lot on the data, 
    # we'll calculate errors for each data size between min_period and max_period
    # and pick up the size which makes the least error
    
    # this will produce a more consistent result over the time

    errors = []

    for i in range(min_period, max_period):
        try:
            first_val = math.log10(cases[cases.size - i - 1])
            data = np.log10(cases[cases.size - i:]) - first_val

            # the latest values have more weight

            sigma = np.flip(func_sigma(np.arange(data.size), q))

            popt, pcov = curve_fit(f, np.arange(data.size), data, sigma=sigma)

            err = np.average(np.square(np.log10(data) - f(np.arange(data.size), *popt)))

            errors.append(err)

        except Exception as e:
            errors.append(np.inf)

    try:
        min_err = np.amin(errors)
        idx = np.argmin(errors)
        period = idx + min_period
    except Exception as e:
        min_err = np.inf
        idx = -1
        period = -1

    return FitErrOutput(min_err, idx, period, errors)


def _get_fit(cases, f, q, period):
    cases_fit = np.array([])
    output = FitOutput()

    try:
        first_val = math.log10(cases[cases.size - period - 1])
        data = np.log10(cases[cases.size - period:]) - first_val

        sigma = np.flip(func_sigma(np.arange(data.size), q))

        popt, pcov = curve_fit(f, np.arange(data.size), data, sigma=sigma)

        offset = cases.size - period

        cases_fit = 10 ** (f(np.arange(-offset, DAYS_TOTAL - offset), *popt) + first_val)

        current_actual = cases[-1]
        current = 10 ** (f(period - 1, *popt) + first_val)
        current_h = 10 ** (f(period - 1 + 1 / 24, *popt) + first_val) - current
        daily_inc = 100 * current_h * 24 / current
        in_1wk = 10 ** (f(period - 1 + 7, *popt) + first_val)
        in_2wk = 10 ** (f(period - 1 + 14, *popt) + first_val)

        output = FitOutput(current_actual, current, current_h, daily_inc, in_1wk, in_2wk)

    except Exception as e:
        pass

    return cases_fit, output


def _get_best_fit(cases, q):
    # compare errors of fitting for f(x) = b * (1 - a ** x) and f(x) = a * x + b functions
    fit_err_exp = _get_fit_errors(cases, func_fit_exp, q, MIN_PERIOD, MAX_PERIOD)
    fit_err_lin = _get_fit_errors(cases, func_fit_lin, q, MIN_PERIOD, MAX_PERIOD)

    # pick up the one with the best fit 
    if fit_err_exp.min_err <= fit_err_lin.min_err:
        cases_fit, fit_output = _get_fit(cases, func_fit_exp, q, fit_err_exp.period)
    else:
        cases_fit, fit_output = _get_fit(cases, func_fit_lin, q, fit_err_lin.period)

    return cases_fit, fit_output


class CovidData(object):

    def plot_actual(self, ax, linestyle='', marker='s', linewidth=2):
        offset = np.full(FILTER_WIN_SIZE // 2, np.nan)
        ax.plot(
            self._actual,
            linestyle=linestyle,
            marker=marker,
            linewidth=linewidth,
            color=self._color
        )

    def plot_fitted(self, ax, linestyle='--', marker='', linewidth=2):
        data = np.copy(self._fitted)
        data[:self._actual.size - 14] = np.nan
        ax.plot(
            data,
            linestyle=linestyle,
            marker=marker,
            linewidth=linewidth,
            color=self._color
        )

    def plot_filtered(self, ax, linestyle='-', marker='', linewidth=2):
        offset = np.full(FILTER_WIN_SIZE // 2, np.nan)
        ax.plot(
            np.concatenate((offset, self._filtered)),
            linestyle=linestyle,
            marker=marker,
            linewidth=linewidth,
            color=self._color
        )

    def plot_daily(self, ax, linestyle='', marker='s', linewidth=2):
        offset = np.full(1, np.nan)
        ax.plot(
            np.concatenate((offset, self._daily)),
            linestyle=linestyle,
            marker=marker,
            linewidth=linewidth,
            color=self._color
        )

    def plot_daily_filtered(self, ax, linestyle='-', marker='', linewidth=4, linestyle_proj='--', marker_proj='', linewidth_proj=4):
        offset = np.full(FILTER_WIN_SIZE // 2 + 1, np.nan)
        ax.plot(
            np.concatenate((offset, self._daily_filtered)),
            linestyle=linestyle,
            marker=marker,
            linewidth=linewidth,
            color=self._color
        )
        ax.plot(
            np.concatenate((offset, self._daily_projected_filtered)),
            linestyle=linestyle_proj,
            marker=marker_proj,
            linewidth=linewidth_proj,
            color=self._color
        )

    @property
    def proj_vals(self):
        return self._proj_vals

    def __init__(self, data, color, q):
        super(CovidData, self).__init__()

        self._color = color

        self._actual = np.array([])
        self._fitted = np.array([])
        self._filtered = np.array([])
        self._daily = np.array([])
        self._daily_filtered = np.array([])
        self._projected = np.array([])
        self._projected_filtered = np.array([])
        self._daily_projected = np.array([])
        self._daily_projected_filtered = np.array([])
        self._proj_vals = ProjectedValues()

        try:
            actual = data
            last_actual = actual[-1]
            l = actual.size

            # calculate 1 week err

            _, fit_output = _get_best_fit(actual[:-7], q)
            err_1wk = 100 * (fit_output.in_1wk - last_actual) / last_actual

            # calculate 2 week err

            _, fit_output = _get_best_fit(actual[:-14], q)
            err_2wk = 100 * (fit_output.in_2wk - last_actual) / last_actual

            # recent

            self._actual = actual

            self._fitted, fit_output = _get_best_fit(actual, q)

            win = hann(FILTER_WIN_SIZE, sym=True)
            win = win / np.sum(win)

            self._filtered = np.convolve(actual, win, mode='valid')

            self._daily = np.diff(actual)

            self._daily_filtered = np.diff(self._filtered)

            self._projected = np.concatenate((actual, self._fitted[l:]))

            self._projected_filtered = np.convolve(self._projected, win, mode='valid')

            self._daily_projected = np.diff(self._projected)

            self._daily_projected_filtered = np.diff(self._projected_filtered)

            current_daily = self._daily_projected[l - 1]
            in_1wk_daily = self._daily_projected[l - 1 + 7]
            in_2wk_daily = self._daily_projected[l - 1 + 14]

            self._proj_vals = ProjectedValues(*fit_output, current_daily, in_1wk_daily, in_2wk_daily, err_1wk, err_2wk)

        except Exception as e:
            if len(data):
                print('>> invalid data')


class Region(object):

    @property
    def cases(self):
        return self._cases

    @property
    def deaths(self):
        return self._deaths

    def __init__(self, name, population, cases_data, death_data, color, q):
        super(Region, self).__init__()

        self._name = name
        self._population = population
        self._color = color

        self._cases = CovidData(cases_data, color, q)
        self._deaths = CovidData(death_data, color, q)
