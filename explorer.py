#!/usr/bin/env python

import pymongo
import matplotlib.pyplot as plt
import os
from collections import namedtuple, defaultdict, deque
from datetime import date
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from graphviz import Graph, Digraph
from itertools import groupby, product
from operator import itemgetter
from utils import _sanitize_username, _sanitize_question


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

    title = 'Last asked without answers histogram' if questions_without_answers_only else 'Last asked histogram'
    _plot_bar(
        x=distinct_dates_without_days,
        y=distinct_dates_without_days_counts,
        filename=filename,
        title=title,
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


# Analyzing which topics are occurring the most frequently
def analyze_topics_frequency(quora_data):
    topics_frequencies = defaultdict(int)
    for document in quora_data:
        question = _get_question(document)
        topics = document[question]['topics']
        for topic in topics:
            topics_frequencies[topic] += 1

    for topic in sorted(topics_frequencies, key=topics_frequencies.get, reverse=True):
        print topic, topics_frequencies[topic]


# Sorting users be specific attribute attribute
def users_by_attribute(quora_data, attribute):
    count_by_attribute = {}
    for document in quora_data:
        username = _get_username(document)
        count_by_attribute[username] = document[username][attribute]
    with open(os.path.join('results', 'users_%s.txt' % attribute), 'w') as f:
        for user in sorted(count_by_attribute, key=count_by_attribute.get, reverse=True):
            f.write(user + ': ' + str(count_by_attribute[user]) + '\n')

# Questions by attribute
def questions_by_attribute(quora_data, attribute, f):
    count_by_attribute = {}
    for document in quora_data:
        question = _get_question(document)
        count_by_attribute[question] = (f(document[question][attribute]), document[question][attribute])
        #print document[question][attribute]
    with open(os.path.join('results', 'questions_%s.txt' % attribute), 'w') as f:
        for question in sorted(count_by_attribute.items(), key=lambda x: x[1][0], reverse=True):
            f.write(str(question) + '\n')


## Starting with root_question e.g. 'what-is-terrorism' graph of questions is explored
## and the goal is to find a path through the graph leading to question with particular
## topic/tag like 'Astronomy'
def explore_questions_by_topic(quora_data, root_question, topic):
    already_explored_questions = set()
    d = {}
    for document in quora_data:
        question = _get_question(document)
        d[question] = document[question]
        d[question]['related_questions'] = [_sanitize_question(x) for x in d[question]['related_questions']]
    
    questions_queue = []
    already_explored_questions.add(root_question)
    questions_queue.append([root_question])

    questions_path = []
    while questions_queue:
        # get the first path from the queue
        questions_path = questions_queue.pop(0)
        # get the last node from the path
        question = questions_path[-1]
        # questions_path found
        print d[question]['topics']
        if topic in d[question]['topics']:
            break
        # enumerate all adjacent nodes, construct a new path and push it into the queue
        for related_question in d[question]['related_questions']:
            if related_question not in already_explored_questions and related_question in d:
                already_explored_questions.add(related_question)
                new_questions_path = list(questions_path)
                new_questions_path.append(related_question)
                questions_queue.append(new_questions_path)

    print 'Path leading to %s : %r' % (topic, questions_path)

styles = {
    'graph': {
        'label': 'Graph',
        'fontsize': '12',
        'fontcolor': 'white',
        'bgcolor': '#888888',
        'overlap': 'prism',
        'outputorder': 'edgesfirst'
        # 'rankdir': 'BT'
    },
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'hexagon',
        'fontcolor': 'white',
        'color': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    },
    'edges': {
        'color': 'black',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '12',
        'fontcolor': 'white',
    }
}


# Visualizing topics using graphviz
# Topics appearing in the same question are linked together
def visualize_topics(quora_data):
    dot = Graph(comment='Topics graph', engine='sfdp')
    seen_topics = set()
    for document in quora_data:
        question = _get_question(document)
        topics = document[question]['topics']
        # Iterating over topics and adding nodes for topics if necessary
        for topic in topics:
            if topic not in seen_topics:
                dot.node(topic, label=topic)
                seen_topics.add(topic)
        # Iterating over topics and adding edges between topics belonging to the same question
        for i in xrange(len(topics)):
            for j in xrange(i+1, len(topics)):
                dot.edge(topics[i], topics[j])
            #     topic1, topic2 in product(topics, topics):
            # dot.edge(topic1, topic2)
    dot = _apply_styles(dot, styles)
    # print dot.source
    dot.render(os.path.join('images', 'topics.gv'), view=True)


# Visualizing network of users (by using followers/following relationship) using graphviz
def visualize_users(quora_data):
    dot = Digraph(comment='Users subgraph', engine='sfdp')
    seen_users = set()
    for document in quora_data:
        username = _get_username(document)
        # Checking if user was already added to the graph
        if username not in seen_users:
            # Adding user to graph as node
            dot.node(username, label=username)
            seen_users.add(username)

    for document in quora_data:
        username = _get_username(document)
        # Traversing over following users and adding edge
        for following in document[username]['following']:
            following_sanitized = _sanitize_username(following)
            if following_sanitized in seen_users:
                dot.edge(username, following_sanitized)
        # Traversing over user's followers
        for follower in document[username]['followers']:
            follower_sanitized = _sanitize_username(follower)
            if follower_sanitized in seen_users:
                dot.edge(follower_sanitized, username)

    dot = _apply_styles(dot, styles)
    # print dot.source
    dot.render(os.path.join('images', 'users.gv'), view=True)

# Visualizing network of users created based on questions and answers i.e.
# There is a link from question author to guy who answered this question
def visualize_questions_and_answers_authors(quora_data):
    dot = Digraph(comment='Authors subgraph', engine='sfdp')
    seen_authors = set()
    for document in quora_data:
        question = _get_question(document)
        question_author = document[question]['question_author']
        if question_author not in seen_authors:
            if is_valid_author(question_author):
                seen_authors.add(question_author)
                dot.node(question_author, label=question_author)

        answers_authors = document[question]['answers_authors']
        for answer_author in answers_authors:
            if answer_author not in seen_authors:
                if is_valid_author(answer_author):
                    seen_authors.add(answer_author)
                    dot.node(answer_author, label=answer_author)
            if question_author in seen_authors and answer_author in seen_authors:
                dot.edge(question_author, answer_author)

    dot = _apply_styles(dot, styles)
    dot.render(os.path.join('images', 'authors.gv'), view=True)

def is_valid_author(authorname):
    return True
    # Uncomment this below to find only authors with normal names
    #return authorname != 'Anonymous' and authorname != '' and authorname != 'User' and authorname !='Quora-User'

def _apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph


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
    return _get(document)


def _get_username(document):
    return _get(document)


def _get(document):
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

    questions_data = list(db.questions.find())
    users_data = list(db.users.find())
    answers_data = list(db.answers.find())
    # create_date_histogram(questions_data)
    # # Considering only questions that have no answers
    # create_date_histogram(
    #     questions_data,
    #     questions_without_answers_only=True,
    #     filename='date_histogram_without_answers_only.png'
    # )
    # create_answer_histogram(quora_data)
    # analyze_topics(questions_data)
    # analyze_topics_frequency(questions_data)
    # visualize_topics(questions_data)
    # visualize_users(users_data)
    # visualize_questions_and_answers_authors(answers_data)
    # users_by_attribute(users_data, 'answers')
    # users_by_attribute(users_data, 'questions')
    # users_by_attribute(users_data, 'edits')
    # users_by_attribute(users_data, 'following_count')
    # users_by_attribute(users_data, 'followers_count')
    # questions_by_attribute(questions_data, 'topics', len)

    #explore_questions_by_topic(questions_data, 'What-is-terrorism', 'Astronomy')
    #explore_questions_by_topic(questions_data, 'What-is-terrorism', 'Communist Party of China')
    explore_questions_by_topic(questions_data, 'What-is-terrorism', 'Google')
    #print quora_data
    #print quora_data[0]

if __name__ == '__main__':
    main()
