import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from constants import *
from coviddata import *
from region import Region


if '--download' in sys.argv:
    download()

PLOT_DEATHS = '--deaths' in sys.argv
PLOT_DAILY = '--daily' in sys.argv

regions = []
errors_1wk = []
errors_2wk = []

fig, ax = plt.subplots()

# column captions

print('Region            1 wk err, %  2 wk err, %')

for i in range(len(REGIONS)):
    g, label, population, name, area = REGIONS[i]

    f = get_global_data if g else get_us_data

    if PLOT_DEATHS:
        r = Region(label, population, [], f(name, area, category='deaths')[:], COLORS[i], Qd)
    else:
        r = Region(label, population, f(name, area)[:], [], COLORS[i], Qc)

    regions.append(r)

    covid_data = r.deaths if PLOT_DEATHS else r.cases

    err_1wk_str = '{:.1f}'.format(covid_data.proj_vals.err_1wk)
    err_2wk_str = '{:.1f}'.format(covid_data.proj_vals.err_2wk)

    # print errors in table

    print_name = r._name + ':' + (' ' * 15)[len(r._name):]
    print_err_1wk = (' ' * 13)[len(err_1wk_str):] + err_1wk_str
    print_err_2wk = (' ' * 13)[len(err_2wk_str):] + err_2wk_str

    print('{}{}{}'.format(print_name, print_err_1wk, print_err_2wk))

    errors_1wk.append(abs(covid_data.proj_vals.err_1wk))
    errors_2wk.append(abs(covid_data.proj_vals.err_2wk))

    if PLOT_DAILY:
        covid_data.plot_daily(ax)
        covid_data.plot_daily_filtered(ax)
    else:
        covid_data.plot_actual(ax)
        covid_data.plot_fitted(ax)
        covid_data.plot_filtered(ax)

# print average values

print('1 wk error average: {:.1f}%'.format(np.average(errors_1wk)))
print('2 wk error average: {:.1f}%'.format(np.average(errors_2wk)))


# save projected values to csv file

with open(PROJ_VALS_FILENAME, 'w', newline='') as csvfile:

    writer = csv.writer(csvfile)

    for r in regions:
        covid_data = r.deaths if PLOT_DEATHS else r.cases
        writer.writerow((r._name, r._color, r._population, *covid_data.proj_vals))


# chart settings

plt.yscale('log')

ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y), 0)))).format(y)))
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: DATES[int(x)] if x > 0 else ''))

if PLOT_DAILY:
    plt.ylim(.8, 12000) if PLOT_DEATHS else plt.ylim(8, 120000)
else:
    plt.ylim(8, 120000) if PLOT_DEATHS else plt.ylim(80, 1200000)

plt.xlim(FIRST_DAY_IDX - DAYS_TOTAL * .02, DAYS_TOTAL - FIRST_DAY_IDX + DAYS_TOTAL * .02)
plt.xticks(TICKS)
plt.tick_params(labelsize=18)
plt.grid(color='#dddddd', linestyle='-', linewidth=1, axis='y')
plt.grid(color='#f5f5f5', linestyle='-', linewidth=1, axis='x')
plt.subplots_adjust(left=.06, bottom=.15, right=.98, top=.88, wspace=None, hspace=None)

# save chart to file with 3040x1720 resolution

my_dpi = 96
fig.set_size_inches(3040 / my_dpi, 1720 / my_dpi)
fig.savefig(IMG_FILENAME, dpi=my_dpi)

plt.show()
