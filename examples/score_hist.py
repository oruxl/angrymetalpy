import datetime as dt

import numpy as np
import matplotlib.pyplot as plt

import angrymetalpy as amp

if __name__ == '__main__':
    reviews = amp.reviews_from_txt('data_20180422.txt')
    min_date, max_date = amp.date_range(reviews)
    num_months = amp.months_between(min_date, max_date) + 1

    sc = []
    sc_past = []
    six_months_ago = dt.datetime.today() - dt.timedelta(6*365/12)

    for rev in reviews:
        sc.append(rev.score)
        if rev.date > six_months_ago:
            sc_past.append(rev.score)

    print(np.mean(sc), np.median(sc))
    fig_hist = plt.figure(figsize=(5,4), dpi=100)
    axhist = fig_hist.add_subplot(111)
    axhist.hist(sc, bins=np.arange(0, 6, step=0.5))
    axhist.set_ylabel('Counts')
    axhist.set_xlabel('Score')
    axhist.set_xlim(0, 5.25)
    axhist.set_title('All Scores')
    xtickpos = 0.25 + np.arange(0, 6, step=0.5)
    plt.xticks(xtickpos, np.arange(0, 6, step=0.5))

    plt.savefig('hist.png', transparent=False, dpi=100)
