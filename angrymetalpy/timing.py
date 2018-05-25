import datetime as dt
import numpy as np

# Useful time-related functions for plotting AMG data

def date_range(review_list):
    """ Find the date range of a set of reviews """
    min_date = None
    max_date = None

    for rev in review_list:
        if min_date is None:
            min_date = rev.date
            max_date = rev.date
            continue

        if rev.date < min_date:
            min_date = rev.date
            continue
        elif rev.date > max_date:
            max_date = rev.date
            continue

    return (min_date, max_date)

def months_between(min_date, max_date):
    """ Return number of months between two datetime objects """
    return 12 * (max_date.year - min_date.year) - min_date.month + max_date.month

def set_month_axis(ax, min_date, max_date, step=12):
    """ Given a Matplotlib axis object, set the x axis to display months """
    num_months = months_between(min_date, max_date) + 1
    xs = np.arange(start=0, stop=num_months, step=1)

    xlabels = []
    yr = min_date.year
    mn = min_date.month
    for i in range(num_months + 1):
        d = dt.datetime(yr, mn, 1)
        xlabels.append(dt.datetime.strftime(d, '%b-%y'))
        mn += 1
        if mn == 13:
            yr += 1
            mn = 1

    xtickpos = xs +  0.5
    # start labels lined up with january of each year
    offset = 13 - min_date.month
    ax.set_xticks(xtickpos[offset::step])
    ax.set_xticklabels(xlabels[offset::step])
    ax.set_xlim(-1, num_months + 1)
