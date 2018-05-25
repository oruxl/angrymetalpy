from datetime import datetime
import matplotlib.pyplot as plt

import numpy as np
import angrymetalpy as amp


if __name__ == '__main__':
    reviews = amp.reviews_from_txt('data_20180422.txt')
    min_date, max_date = amp.date_range(reviews)
    num_months = amp.months_between(min_date, max_date) + 1

    genres = set(['Death Metal', 'Black Metal', 'Doom Metal', 'Progressive Metal', 'Folk Metal', 'Thrash Metal', 'Hardcore', 'Hard Rock'])

    fig = plt.figure(figsize=(7,5))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, num_months)


    for genre in genres:
        scores = np.zeros(num_months)
        counts = np.zeros(num_months)

        for rev in reviews:
            if genre not in rev.tags:
                continue
            #if len(list(genre & set(rev.tags))) > 1:
            #    continue
            idx = amp.months_between(min_date, rev.date)
            scores[idx] += rev.score
            counts[idx] += 1

        scores /= counts # average scores per month

        xs = np.arange(start=0, stop=num_months, step=1)

        month_bin = 12
        binned_xs = xs[::month_bin][1:]
        binned_scores = np.zeros(len(binned_xs))
        for i in range(len(binned_xs)):
            scores_in_range = [_ for _ in scores[month_bin * i:][:month_bin] if not np.isnan(_)]
            if len(scores_in_range) > 0:
                binned_scores[i] = np.sum(scores_in_range) / len(scores_in_range)
            else:
                binned_scores[i] = np.nan

        ax.plot(binned_xs, binned_scores, '-', lw=2, label=genre)
        # ax.plot(xs, scores, '-', lw=2, label=genre)

    amp.set_month_axis(ax, min_date, max_date)
    #ax.set_ylabel('Average Review Scores')
    plt.legend(loc='best')

    plt.savefig('genre_score.pdf')
