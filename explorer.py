#!/usr/bin/env python

import pymongo
import matplotlib.pyplot as plt
import os
from collections import namedtuple
from datetime import date
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from itertools import groupby
import os

# This is needed when obtaining date for last Monday, Tuesday, etc.
WEEKDAYS = {'Mon': MO(-1), 'Tue': TU(-1), 'Wed': WE(-1), 'Thu': TH(-1),
            'Fri': FR(-1), 'Sat': SA(-1), 'Sun': SU(-1)}

# Ordering months.
MONTHS = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
          'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

# Getting current year
CURR_YEAR = date.today().year

# Convenience data structure for holding date
Date = namedtuple('Date', ['day', 'month', 'year'], verbose=False)


def create_date_histogram(quora_data, questions_without_answers_only=False, filename='date_histogram.png'):
    """
    :param quora_data: Collection of documents (list) related to questions
    :param questions_without_answers_only: if True then we collect information only about questions w/o answers
    :return: None
    """
    # List of dates (when questions were last asked)
    dates = []
    for document in quora_data:
        question = _get_question(document)
        #print question
        answer_count = document[question]['answer_count']

        # This code should be skipped precisely when question has some answers
        # and we are considering questions with answers.
        if not questions_without_answers_only or answer_count == 0:
            last_asked = document[question]['last_asked']
            #print last_asked
            date = _parse_date(last_asked)
            #print date
            dates.append(date)

    dates = sorted(dates, key=lambda x: (x.year, x.month, x.day))
    #print dates

    dates_without_days = ['%02d/%d' % (x.month, x.year) for x in dates]
    #print dates_without_days
    # Removing consecutive duplicates while preserving order !
    distinct_dates_without_days = [x[0] for x in groupby(dates_without_days)]
    #print distinct_dates_without_days
    distinct_dates_without_days_counts = [dates_without_days.count(x) for x in distinct_dates_without_days]
    #print distinct_dates_without_days_counts
    _plot_bar(
        x=distinct_dates_without_days,
        y=distinct_dates_without_days_counts,
        filename=filename,
        title='Last asked histogram',
        xlabel='Last asked',
        ylabel='Frequency'
    )


def create_answer_histogram(quora_data):
    # List of answer counts (counters counting number of answers for particular question)
    answer_counts = []
    for document in quora_data:
        question = _get_question(document)
        answer_count = document[question]['answer_count']
        #print answer_count
        answer_counts.append(answer_count)

    #print answer_counts

    _plot_histogram(
        x=answer_counts,
        filename='answer_count_histogram.png',
        title='Answer count histogram',
        xlabel='Answer count',
        ylabel='Frequency',
        bins=10
    )


# Analyzing topics / tags
def analyze_topics(quora_data):
    all_topics = set([])
    for document in quora_data:
        question = _get_question(document)
        topics = document[question]['topics']
        for topic in topics:
            all_topics.add(topic)
    # Sorting topics/tags and printing them out
    sorted_topics = sorted(list(all_topics))
    print '-------------------------------------'
    print 'List of topics in alphabetical order:'
    for topic in sorted_topics:
        print topic


def _plot_bar(x, y, filename='tmp.png', title='title', xlabel='X', ylabel='Y'):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Some dummy values that will be replaced by labels when plotting
    x_indexes = range(len(x))
    plt.bar(x_indexes, y, align='center')
    plt.xticks(x_indexes, x, rotation=70)
    plt.gcf().set_size_inches(20, 12)
    plt.savefig(os.path.join('images', filename), dpi=100)
    plt.show()


def _plot_histogram(x, filename='tmp.png', title='title', xlabel='X', ylabel='Y', bins=5):
    plt.hist(x, bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.gcf().set_size_inches(20, 12)
    plt.savefig(os.path.join('images', filename), dpi=100)
    plt.show()


def _parse_date(last_asked):
    """
    :param last_asked: Quora funky way of saying you when the question was submitted - format is roughly unknown
    :return: When question was asked (date) in format (DAY, MONTH, YEAR)
    """
    datetime = last_asked.strip().split()

    # Only day of the week is provided like: Mon
    if len(datetime) == 1:
        last_weekday = date.today() + relativedelta(weekday=WEEKDAYS[datetime[0]])
        day = last_weekday.day
        month = last_weekday.month
        year = last_weekday.year

    if len(datetime) >= 2:
        day = int(datetime[0])
        if datetime[1] in MONTHS:
            month = MONTHS[datetime[1]]
        year = CURR_YEAR

    # Expecting this type of date: 12 Jun
    if len(datetime) == 2:
        year = CURR_YEAR
    # Expecting date with year: 3 Mar 1991
    elif len(datetime) == 3:
        year = int(datetime[2])

    return Date(day, month, year)


def _get_question(document):
    keys = document.keys()
    if keys[0] != '_id':
        return keys[0]
    else:
        return keys[1]


def main():
    connection_str = 'mongodb://localhost:27017/'
    quora_db = 'quora'
    client = pymongo.MongoClient(connection_str)
    db = client[quora_db]

    quora_data = list(db.questions.find())
    create_date_histogram(quora_data)
    # Considering only questions that have no answers
    create_date_histogram(
        quora_data,
        questions_without_answers_only=True,
        filename='date_histogram_without_answers_only.png'
    )
    create_answer_histogram(quora_data)
    analyze_topics(quora_data)
    #print quora_data
    #print quora_data[0]

if __name__ == '__main__':
    main()