import numpy as np
import matplotlib.pyplot as plt

import angrymetalpy as amp

if __name__ == '__main__':
    reviews = amp.reviews_from_txt('data_20180422.txt')

    # we want to build a correlation plot for pairs of tags
    # start by finding all tags we are dealing with
    all_tags = set()
    for rev in reviews:
        for tag in rev.tags:
            all_tags.add(tag)

    # create a 2d matrix of zeros to be filled
    all_tags = list(all_tags)
    tag_counts = np.zeros(len(all_tags), dtype=int)

    for rev in reviews:
        for tag in rev.tags:
            tag_counts[all_tags.index(tag)] += 1

    all_tags = sorted(zip(tag_counts, all_tags), key=lambda x: x[0], reverse=True)[:40]
    _, all_tags = zip(*all_tags)

    # alphabetize the list
    all_tags = sorted(all_tags)

    arr = np.zeros(shape=(len(all_tags), len(all_tags)), dtype=int)

    # fill the histogram
    for rev in reviews:
        for tag1 in rev.tags:
            for tag2 in rev.tags:
                try:
                    i = all_tags.index(tag1)
                    j = all_tags.index(tag2)
                except ValueError:
                    continue
                if j > i:
                    break

                if i != j:
                    arr[i][j] += 1

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_xlim(0, len(all_tags))
    ax.set_ylim(0, len(all_tags))
    ax.set_xticklabels(all_tags, rotation='vertical')
    ax.set_yticklabels(all_tags)

    xbins = np.arange(0, len(all_tags) + 1, step=1)
    ybins = np.arange(0, len(all_tags) + 1, step=1)
    ax.xaxis.set_ticks_position('top')
    xtickpos = xbins +  0.5
    ytickpos = ybins +  0.5
    ax.set_xticks(xtickpos)
    ax.set_yticks(ytickpos)

    pcm = ax.pcolormesh(xbins, ybins, arr)
    fig.colorbar(pcm, ax=ax)

    plt.savefig('tag_correlation.pdf')
