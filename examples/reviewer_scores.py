from datetime import datetime
import matplotlib.pyplot as plt

import numpy as np
import angrymetalpy as amp


if __name__ == '__main__':
    reviews = amp.reviews_from_txt('data_20180422.txt')
    amg_reviewers = amp.reviewers_from_reviews(reviews)

    amg_reviewers = sorted(amg_reviewers, key=lambda x: len(x.reviews))

    fig = plt.figure()
    ax = fig.add_subplot(111)

    min_date, max_date = amp.date_range(reviews)
    n_months = amp.months_between(min_date, max_date)

    xs = np.arange(start=0, stop=n_months, step=1)
    # timeline of reviewer activity
    for i, reviewer in enumerate(amg_reviewers):
        ys = np.zeros(n_months)
        ys_counts = np.zeros(n_months)
        for review in reviewer.reviews:
            idx = amp.months_between(min_date, review.date)
            ys[idx - 1] += review.score
            ys_counts[idx - 1] += 1

        idxs = np.where(ys_counts > 3)
        ys[idxs] /= ys_counts[idxs]

        if len(idxs[0]) > 1:
            ax.plot(xs[idxs], ys[idxs], '.', label=reviewer.name)

    amp.set_month_axis(ax, min_date, max_date, step=12)

    ax.set_ylabel('Average scores of reviewers with > 3 reviews/month')
    ax.set_title('Brutality vs. Time')

    ax.legend(loc='best', ncol=5, fontsize=10)

    plt.savefig('scores.pdf')
