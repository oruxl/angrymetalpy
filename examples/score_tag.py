from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

import numpy as np
import angrymetalpy as amp


if __name__ == '__main__':
    reviews = amp.reviews_from_json('data_20180422.txt')
    min_date, max_date = amp.date_range(reviews)
    num_months = amp.months_between(min_date, max_date) + 1

    scores = np.zeros(num_months)
    counts = np.zeros(num_months)

    for rev in reviews:
        idx = amp.months_between(min_date, rev.date)
        scores[idx] += rev.score
        counts[idx] += 1

    scores /= counts # average scores per month
    score_unc = np.sqrt(counts) / counts

    fig = plt.figure(figsize=(7,5))
    rect = (1, 1, 1, 1)
    ax2 = fig.add_axes(rect, label='axis2')
    ax1 = fig.add_axes(rect, label='axis1')
    ax1.set_xlim(0, num_months)
    ax2.set_xlim(0, num_months)
    ax1.yaxis.set_ticks_position('left')
    ax2.yaxis.set_ticks_position('right')
    ax2.yaxis.set_label_position('right')
    ax2.xaxis.set_major_formatter(NullFormatter())
    ax2.xaxis.set_ticks_position('none')

    xs = np.arange(start=0, stop=num_months, step=1)
    ax1.plot(xs, scores, '-', lw=2, color='r', label='Avg. Score')
    ax1.fill_between(xs, scores - score_unc, scores + score_unc, lw=0, alpha=0.5)
    ax2.plot(xs, counts, '-', lw=2, color='b', label='Reviews per Month')

    amp.set_month_axis(ax1, min_date, max_date)

    ax1.yaxis.set_tick_params(labelcolor='r', color='r')
    ax2.yaxis.set_tick_params(labelcolor='b', color='b')
    ax1.set_ylabel('Average Review Scores', color='r')
    ax2.set_ylabel('Reviews per Month', color='b')
    #ax.set_title('Brutality vs. Time')

    plt.savefig('avg_score_v_time.pdf')
