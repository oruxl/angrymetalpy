#
# timeline.py
# create a 2d histogram of review count vs time for each AMG reviewer
#

from datetime import datetime
import matplotlib.pyplot as plt

import numpy as np
import angrymetalpy as amp


if __name__ == '__main__':
    reviews = amp.reviews_from_txt('data_20180422.txt')
    amg_reviewers = amp.reviewers_from_reviews(reviews)

    amg_reviewers = sorted(amg_reviewers, key=lambda x: len(x.reviews))

    fig = plt.figure(figsize=(5, 8), dpi=100)
    ax = fig.add_subplot(111)

    min_date, max_date = amp.date_range(reviews)
    n_months = amp.months_between(min_date, max_date)

    # timeline of reviewer activity
    xs = []
    ys = []
    for i, reviewer in enumerate(amg_reviewers):
        for review in reviewer.reviews:
            xs.append(amp.months_between(min_date, review.date))
            ys.append(i)

    xbins = np.arange(0, n_months + 1, 1)
    ybins = np.arange(0, len(amg_reviewers) + 1, 1)
    ax.hist2d(xs, ys, bins=[xbins, ybins])
    ax.set_ylim(0, len(amg_reviewers) - 0.5)

    # y axis should line up reviewer names with rows
    ylabels = [x.name for x in amg_reviewers]
    ytickpos = ybins +  0.5
    ax.set_yticks(ytickpos)
    ax.set_yticklabels(ylabels)

    amp.set_month_axis(ax, min_date, max_date, step=24)

    plt.savefig('timeline.png', transparent=False, dpi=100)
