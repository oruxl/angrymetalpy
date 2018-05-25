# Scrape data from AMG review pages.
#
# This can take a long time, so ideally this is only run once
# Also included is an update function which stops when it finds a review that
# is already in a file.

from lxml import html
from lxml.etree import tostring
from itertools import chain
import requests
import sys
from datetime import datetime
import re

import angrymetalpy as amp

def stringify_children(node):
    """ Converts content within a tag to text even if inside another tag """
    parts = ([node.text] +
            list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
            [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))

def get_review_url(start_page=1, end_page=None):
    """ Returns a list of review page urls from AMG """
    baseurl = 'http://www.angrymetalguy.com/category/reviews/'
    urllist = []

    if end_page is None:
        # user only wants reviews from a specific page
        end_page = start_page + 1

    # Get 5 pages of reviews
    for i in range(start_page, end_page):
        URL = baseurl
        if i > 1:
            URL += 'page/' + str(i) + '/'
        try:
            page = requests.get(URL, timeout=2.0)
        except:
            return None

        try:
            tree = html.fromstring(page.content)
        except:
            return None

        urls = tree.xpath('//a[@class="post-thumb img fix"]/@href')
        for i in range(len(urls)):
            urllist.append(urls[i])

    return urllist

def get_page_data(URL):
    """ Scrape score from each review page """
    try:
    	page = requests.get(URL, timeout=10.0)
    except:
        return

    try:
        tree = html.fromstring(page.content)
    except:
        return

    # some reviews use the unicode '-' character, u2013, so we have to replace it before splitting
    try:
        album_artist = tree.xpath('//title/text()')[0].strip().replace(u'\u2013', '-').split(' Review')[0]
        artist = album_artist.split(' - ')[0]
        album = album_artist.split(' - ')[1]
    except:
        print('Could not get album/artist info from {}'.format(URL))
        artist = ''
        album = ''

    author = tree.xpath('//a[@rel="author"]/text()')[0] # name of reviewer
    date = tree.xpath('//time[@class="date time published updated sc"]/text()')[0] # date of review
    date_as_obj =  datetime.strptime(date, "%B %d, %Y")
    taglist = tree.xpath('//meta[@property="article:tag"]/@content') # all tag fields

    scorep = None
    scorestr = ''

    # try to find score, or skip things you might have missed reviews
    for tag in taglist:
        score_search = re.search('(\d\.\d)', tag)
        if score_search is not None:
            scorestr = score_search.group(0)

        if 'things you might have missed' in tag.lower():
            return None

    # if score not in the tag, find it the old fashioned way
    if scorestr == '':
        # score text box is almost always a <p> preceded by a horizontal rule
        try:
            scorep = stringify_children(tree.xpath("//hr/following-sibling::p[1]")[0])
        except IndexError:
            # ... but sometimes it's a div
            try:
                scorep = stringify_children(tree.xpath("//hr/following-sibling::div[1]")[0])
            except IndexError:
                # ... and sometimes there is no horizontal rule, so we look for center-justified text
                try:
                    scorep = stringify_children(tree.xpath('//p[@style="text-align: center;"]')[0])
                except IndexError:
                    # otherwise we got nothing
                    scorestr = '-1'

        if scorep is not None:
            score_search = re.search('(\d\.\d\/5.0)', scorep)
            if score_search is not None:
                scorestr = score_search.group(0).split('/5.0')[0]
            else:
                # try to see if any line in the <p> contains an AMG score keyword that
                # we can convert to a score
                scorep = scorep.split('<br/>')
                scorestr = ''
                for elem in scorep:
                    elem = elem.strip().split('!')[0] # some cleanup of the string...
                    for keyword in amp.amg_score_mapping.keys():
                        # technically this section is incorrect because "good" will also find "very good"
                        # however the key list has "very good" first, so it should break before checking "good"
                        score_search = re.search(keyword, elem, flags=re.IGNORECASE)
                        if score_search is not None:
                            scorestr = str(amp.amg_score_mapping[score_search.group(0).lower()])
                            break

                    if scorestr != '':
                        break

    try:
        score = float(scorestr)
    except:
        print('Could not get score from {}'.format(URL))
        score = -1

    try:
        # metal bands use unicode characters
        album, artist, author = (_.encode('utf-8') for _ in [album, artist, author])
        review = amp.Review(album, artist, author, date_as_obj, taglist, score, '')
        return review
    except UnicodeEncodeError:
        print('Unicode error: {}'.format(URL))

def update(prev_file='', max_page=None):
    """ Scrape data. If a filename is specified, only scrape until the program
        encounters a review already in the file. """
    if prev_file != '':
        reviews = amp.reviews_from_txt(prev_file)
        review_titles = [_.album for _ in reviews]

    filename = 'data_{}.txt'.format(
        datetime.strftime(datetime.now(), format='%Y%m%d')) if prev_file == '' else prev_file

    with open(filename, 'a') as f:

        page_count = 1
        found_end = False
        while not found_end:
            urls = get_review_url(start_page=page_count)
            print('found {} reviews on page {}'.format(len(urls), page_count))

            for url in urls:
                rev = get_page_data(url)
                if rev is not None:
                    if prev_file != '':
                        # check if this review was already in prev_file
                        if rev.album in review_titles:
                            # if yes, don't write it and mark this page as the end
                            found_end = True
                            continue

                    # else write to the file
                    print('writing {}'.format(rev.album))
                    f.write(rev.json() + '\n')

            page_count += 1
            if max_page is not None:
                if page_count > max_page:
                    found_end = True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        update(sys.argv[1])
    else:
        update()
