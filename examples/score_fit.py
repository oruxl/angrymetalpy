# do a time series analysis of AMG review score data
#
# - detrend time series using scipy optimize to do a linear fit
# - plot acf of residuals
# - look at fits to subsets of reviews by genre

from datetime import datetime
from matplotlib import gridspec
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
from scipy import optimize

import numpy as np
import angrymetalpy as amp


def linear_model(p,x):
    return p[0] + x*p[1]

def residual(p, x, y, err):
    return (linear_model(p, x)-y)/err


if __name__ == '__main__':
    reviews = amp.reviews_from_json('data_20180422.txt')
    min_date, max_date = amp.date_range(reviews)
    num_months = amp.months_between(min_date, max_date) + 1

    # time series
    t = np.arange(start=0, stop=num_months, step=1)
    scores = np.zeros(num_months)
    counts = np.zeros(num_months)

    for rev in reviews:
        idx = amp.months_between(min_date, rev.date)
        scores[idx] += rev.score
        counts[idx] += 1

    scores /= counts # average scores per month
    scores_err = np.sqrt(counts) / counts

    min_idx = np.argmin(scores)
    for rev in reviews:
        idx = amp.months_between(min_date, rev.date)
        if idx == min_idx:
            print(rev.date)
            print(rev.album, rev.artist, rev.score)


    # Figure 1: linear fit
    p0 = [3., -0.005]
    pf, cov, info, mesg, success = optimize.leastsq(residual, p0,
                                         args=(t, scores, scores_err), full_output=1)

    chisq = sum(info["fvec"]*info["fvec"])
    dof = len(t)-len(pf)
    pferr = [np.sqrt(cov[i,i]) for i in range(len(pf))]
    global_fit = (pf[1], pferr[1])

    fig_fit = plt.figure(1, figsize=(5,4), dpi=100)#figsize=(7,5))
    ax = fig_fit.add_subplot(111)
    ax.set_xlim(-1, num_months)

    ax.errorbar(t, scores, yerr=scores_err, fmt='.', color='k', label='Data')

    fit_pts = np.linspace(min(t), max(t), 2)
    ax.plot(fit_pts, linear_model(pf, fit_pts), color='r', label='Fit')

    amp.set_month_axis(ax, min_date, max_date, step=24)
    ax.set_xlabel('Time')
    ax.set_ylabel('Average Review Score per Month')

    plt.savefig('avg_score_fit.png', transparent=False, dpi=100)

    # Figure 2: Residuals
    fig_res = plt.figure(2)
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    gs.update(wspace=0.025, hspace=0.05)

    ax2 = fig_res.add_subplot(gs[0])
    ax2hist = fig_res.add_subplot(gs[1])

    ax2.set_xlim(-1, num_months)
    residuals = scores - linear_model(pf, t)
    ax2.plot(t, residuals, '.')
    ax2hist.hist(residuals, bins=15, alpha=0.5, orientation='horizontal')

    ax2hist.yaxis.set_major_formatter(NullFormatter())
    amp.set_month_axis(ax2, min_date, max_date, step=12)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Fit residual')
    ax2hist.set_xlabel('Counts')

    plt.savefig('avg_score_res.pdf')

    # Figure 3: Residual ACF
    fig_acf = plt.figure(3, figsize=(5,4), dpi=100)
    ax3 = fig_acf.add_subplot(111)
    ax3.set_xlim(-1, num_months)
    ax3.acorr(residuals, maxlags=20)

    ax3.set_xlim(-1, 20)
    ax3.set_ylim(-0.25, 1.05)
    ax3.set_xlabel('Lag')
    ax3.set_ylabel('Residual ACF')

    plt.savefig('avg_score_acf.png', transparent=False, dpi=100)

    # Figure 4: Genre correlations
    fig_genre = plt.figure(4, figsize=(5,4), dpi=100)
    ax4 = fig_genre.add_subplot(111)

    genres = ['Death Metal', 'Black Metal', 'Doom Metal', 'Progressive Metal',
                'Folk Metal', 'Thrash Metal', 'Heavy Metal', 'Hardcore',
                'Power Metal', 'Hard Rock']
    corrs = []
    corr_err = []
    total_counts = []

    for genre in genres:
        scores = np.zeros(num_months)
        counts = np.zeros(num_months)

        for rev in reviews:
            if genre not in rev.tags:
                continue
            idx = amp.months_between(min_date, rev.date)
            scores[idx] += rev.score
            counts[idx] += 1

        print('{} | {:.2f} +/- {:.2f}'.format(genre, sum(scores) / sum(counts), np.sqrt(sum(counts))/sum(counts)))
        scores /= counts # average scores per month
        scores_err = np.sqrt(counts) / counts

        # prune out months with no reviews of this genre
        _t = t[~np.isnan(scores)]
        _scores = scores[~np.isnan(scores)]
        _scores_err = scores_err[~np.isnan(scores)]

        # now we fit the scores with a linear model
        p0 = [3., 0.2]
        pf, cov, info, mesg, success = optimize.leastsq(residual, p0,
                                             args=(_t, _scores, _scores_err), full_output=1)
        pferr = [np.sqrt(cov[i,i]) for i in range(len(pf))]

        corrs.append(pf[1])
        corr_err.append(pferr[1])
        total_counts.append(sum(counts))

    zipped = sorted(zip(genres, corrs, corr_err, total_counts), key=lambda x: x[3], reverse=True)
    genres, corrs, corr_err, total_counts = zip(*zipped)

    ax4.errorbar(range(len(genres)), corrs, yerr=corr_err, fmt='.')
    ax4.axhspan(global_fit[0] - global_fit[1], global_fit[0] + global_fit[1],
                color='r', alpha=0.5, label='All genres')
    ax4.plot([-0.5, len(genres) - 0.5], [0, 0], 'b--')
    ax4.set_xlim(-0.5, len(genres) - 0.5)
    ax4.set_ylabel('Change in Average Score per Month')
    ax4.set_xticks(range(len(genres)))
    ax4.set_xticklabels(genres, rotation='vertical')

    plt.legend(loc='best')
    plt.savefig('avg_score_corr.png', transparent=False, dpi=100)
