import json
import datetime as dt
import numpy as np
import csv
from StringIO import StringIO

# These are the interpretation of the scores listed on the site
# Could be useful for something...
site_score_mapping = {
    'perfect': 5.0,
    'excellent': 4.5,
    'great': 4.0,
    'very good': 3.5,
    'good': 3.0,
    'mixed': 2.5,
    'disappointing': 2.0,
    'bad': 1.5,
    'embarrassing': 1.0,
    'pathetic': 0.5,
    'worthless': 0.0,
}


class _SetEncoder(json.JSONEncoder):
    ''' Helper class to allow the json library to serialize set objects '''
    def default(self, obj):
       if isinstance(obj, set):
          return list(obj)
       return json.JSONEncoder.default(self, obj)


class Review(object):
    def __init__(self, album, artist, author, date, tags, score, text):
         # found that some albums have an extra ending
        self._album = album.split(' | Angry Metal Guy')[0].strip()
        self._artist = artist
        self._author = author
        self._date = date
        self._tags = tags
        self._score = score

        # some reviews are unscored, so we set a flag
        if self._score == -1:
            self._scored = False
        else:
            self._scored = True

        self._text = text

        self._filter_tags()

    def __repr__(self):
        return 'Review of {} by {}. Reviewer: {} on {}. Score: {}'.format(
            self._album, self._artist, self._author,
            dt.datetime.strftime(self._date, "%Y-%m-%d"), self._score
        )

    def is_valid(self):
        """ True if all fields were filled successfully """
        return self._album != "" and self._artist != "" and \
                self._author != "" and self._date is not None and \
                self._score != -1

    def _filter_tags(self):
        """
        Remove numbers and dates from tag list. Private method because
        this should be done while creating the review object
        """
        newtags = set()
        for tag in self._tags:
            # see if the tag is a number
            try:
                tag = float(tag)
                continue
            except ValueError:
                pass

            # cut out generic tags
            if tag.lower() == "review" or tag.lower() == "reviews":
                continue
            if tag.lower() == "release" or tag.lower() == "releases":
                continue

            # cut out tags of the form e.g. Mar2016 or Mar16
            try:
                dt.datetime.strptime(tag, "%b%y")
                continue
            except ValueError:
                pass
            try:
                dt.datetime.strptime(tag, "%b%Y")
                continue
            except ValueError:
                pass

            newtags.add(tag)

        self._tags = newtags

    def json(self):
        json_dict = {
            'album': self._album,
            'artist': self._artist,
            'author': self._author,
            'date': dt.datetime.strftime(self._date, "%Y-%m-%d"),
            'tags': self._tags,
            'score': self._score,
        }
        return json.dumps(json_dict, cls=_SetEncoder, indent=4, sort_keys=True)

    def csv(self):

        def escape(string):
            esc_string = "\"" + string + "\""
	    if type(esc_string) != unicode:
		esc_string =  esc_string.decode('utf-8')
	    return esc_string

        tag_string = escape(';'.join(self._tags))
        csv_fields = [
            escape(self._album), escape(self._artist), 
            escape(self._author), 
            dt.datetime.strftime(self._date, "%Y-%m-%d"), 
            tag_string, str(self._score)
        ]

        return ','.join(csv_fields)

    @property
    def album(self):
        return self._album

    @property
    def artist(self):
        return self._artist

    @property
    def author(self):
        return self._author

    @property
    def score(self):
        return self._score

    @property
    def tags(self):
        return self._tags

    @author.setter
    def author(self, val):
        self._author = val

    @property
    def date(self):
        return self._date

    @staticmethod
    def from_json(string):
        """ Create a review object from a JSON string """
        try:
            json_dict = json.loads(string)
            rev = Review(json_dict['album'].encode('utf-8'),
                         json_dict['artist'].encode('utf-8'),
                         json_dict['author'].encode('utf-8'),
                         dt.datetime.strptime(json_dict['date'], '%Y-%m-%d'),
                         set(json_dict['tags']), json_dict['score'], '')
            return rev
        except Exception as e:
            raise ValueError

    @staticmethod
    def from_csv(string):
        """ Create a review object from a CSV string """

	def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	    for row in csv_reader:
		yield [unicode(cell, 'utf-8') for cell in row]

        line = StringIO(string)
        csv_parse = unicode_csv_reader(line, quotechar='"')

        def unescape(_str):
            try:
                _str = _str.encode('utf-8')
            except:
                pass

            if _str[0] == '\"' and _str[:-1] == '\"':
                return _str[1:-2]
            return _str

        rev = None
        for info in csv_parse:
            try:
                album = unescape(info[0])
                artist = unescape(info[1])
                author = unescape(info[2])
                date = dt.datetime.strptime(info[3], '%Y-%m-%d')
                tags = unescape(info[4]).split(';')
                score = float(info[5])

                rev = Review(album, artist, author, date, set(tags), score, '')
            except Exception as e:
                raise ValueError

        return rev


class Reviewer(object):
    def __init__(self, name):
        self._name = name
        self._reviews = set()

    @property
    def name(self):
        return self._name

    @property
    def reviews(self):
        return self._reviews

    def add_review(self, review):
        """ Associate a review with this reviewer """
        if review.author != '' and review.author != self._name:
            print('Warning: Overwriting review author field.')
        review.author = self._name
        self._reviews.add(review)

    def tag_list(self):
        tagset = set()
        for review in self._reviews:
            for tag in review.tags:
                tagset.add(tag)

        return list(tagset)

    def tag_counts(self, sort='a'):
        the_tags = self.tag_list()
        tag_counts = np.zeros(len(the_tags), dtype=int)

        for review in self._reviews:
            for tag in review.tags:
                tag_counts[the_tags.index(tag)] += 1

        # user may pass 'a' or 'd' to sort ascending or descending
        rev = True if sort == 'd' else False
        return sorted(zip(the_tags, tag_counts), key=lambda x: x[1], reverse=rev)

    def score_list(self):
        scorelist = []
        for review in self._reviews:
            scorelist.append(review.score)

        return np.asarray(scorelist)

    def score_counts(self):
        scorehist = np.zeros(11) # always [0, 5.0] in 0.5 steps
        for review in self._reviews:
            scorehist[int(review.score * 2)] += 1

        return scorehist


def reviews_from_json(fname):
    """ Return a list of reviews from a text file containing JSON dumps of review objects """
    reviews = []
    with open(fname, 'r') as f:
        for line in f:
            # skip header
            if line[0] == '#':
                continue
            while True:
                try:
                    rev = Review.from_json(line)
                    if rev.is_valid():
                        # filter out unscored reviews
                        reviews.append(rev)
                    break
                except ValueError:
                    # Not yet a complete JSON value
                    line += next(f)

    return reviews

def reviews_from_csv(fname):
    """ Return a list of reviews from a text file containing csv-style review info """
    reviews = []
    with open(fname, 'r') as f:
        for line in f:
            #try:
            rev = Review.from_csv(line)
            if rev.is_valid():
                reviews.append(rev)
            #except ValueError:
            #    pass

    return reviews

def reviewers_from_reviews(rev_list):
    """ Returns a list of reviewers inferred from the author field of
        each review in a review list """
    amg_reviewers = []
    for rev in rev_list:
        if rev.score == -1 or rev._album == '':
            continue

        if rev.author not in [_.name for _ in amg_reviewers]:
            amg_reviewers.append(Reviewer(rev.author))

        for reviewer in amg_reviewers:
            if reviewer.name == rev.author:
                reviewer.add_review(rev)
                break

    return amg_reviewers
