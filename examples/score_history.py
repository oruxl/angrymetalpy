from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
from matplotlib import lines

import numpy as np
import angrymetalpy as amp


if __name__ == '__main__':
    reviews = amp.reviews_from_json('data_20180422.txt')
    print(len(reviews))
    min_date, max_date = amp.date_range(reviews)
    num_months = amp.months_between(min_date, max_date) + 1

    scores = np.zeros(num_months)
    counts = np.zeros(num_months)
    perfect_albums = [[] for _ in range(num_months)]

    for rev in reviews:
        idx = amp.months_between(min_date, rev.date)
        scores[idx] += rev.score
        counts[idx] += 1
        if rev.score == 5.0:
            perfect_albums[idx].append(rev.album)

    scores /= counts # average scores per month
    score_unc = np.sqrt(counts) / counts

    fig = plt.figure(figsize=(5,4), dpi=100)
    rect = (1, 1, 1, 1)
    #ax2 = fig.add_axes(rect, label='axis2')
    ax1 = fig.add_axes(rect, label='axis1')
    ax1.set_xlim(0, num_months)
    #ax2.set_xlim(0, num_months)
    ax1.yaxis.set_ticks_position('left')
    #ax2.yaxis.set_ticks_position('right')
    #ax2.yaxis.set_label_position('right')
    #ax2.xaxis.set_major_formatter(NullFormatter())
    #ax2.xaxis.set_ticks_position('none')

    xs = np.arange(start=0, stop=num_months, step=1)
    #ax1.plot(xs, scores, '-', lw=2, color='r', label='Avg. Score')
    #ax1.fill_between(xs, scores - score_unc, scores + score_unc, lw=0, alpha=0.5)

    ax1.plot(xs, counts, '-', lw=2, color='b', label='Reviews per Month')

    perf_x = []
    prev_perfect = -10
    #flip = True
    for time, albums in enumerate(perfect_albums):
        txt = ' & '.join([album.decode('utf-8') for album in albums])
        if txt == '':
            continue
        perf_x.append(time)

        print(time-prev_perfect)
        x = time if time - prev_perfect > 2 else prev_perfect + 4

        y = 90.65 if x == time else 93
        align = 'bottom'#'top' if flip else 'bottom'
        ax1.plot([time, time], [0, 92], '-', color='g')
        if x != time:
            ax1.annotate('', xy=(time, 89.9), xytext=(x, 92.55),
                arrowprops=dict(arrowstyle="-", color='g', alpha=1.0, lw=1, ls='-'))
            #ax1.plot([time, x], [0, 92], '--', color='g')

        ax1.text(x, y, txt, color='g',
                fontsize=10, horizontalalignment='center', verticalalignment=align, rotation='vertical')

        prev_perfect = x#time #if not flip else prev_perfect

    ax1.set_ylim(0,90)

    #ax1.plot(perf_x, counts[perf_x], '*', color='b', lw=0)
    amp.set_month_axis(ax1, min_date, max_date, step=24)

    #ax1.yaxis.set_tick_params(labelcolor='r', color='r')
    #ax2.yaxis.set_tick_params(labelcolor='b', color='b')
    ax1.set_ylabel('Reviews per Month')#, color='r')
    #ax2.set_ylabel('Reviews per Month', color='b')
    #ax.set_title('Brutality vs. Time')

    plt.savefig('avg_score_v_time.png', transparent=False, dpi=100)
