import pymongo
import re
from pyquora.quora import Quora
__author__ = 'michal3141'


def _sanitize_question(question):
    """
    :param question: question to be sanitized e.g. 'what is terrorism'
    :return: sanitized question e.g. 'what-is-terrorism'
    """
    return re.sub(r'(\W)\1+', r'\1', question.replace(' ', '-').replace('?', '').replace(',', '').replace('/', '-') \
        .replace("'", '').replace('.', '').replace(':', '').replace('(', '').replace(')', '') \
        .replace('"', ''))


class Crawler(object):
    def __init__(self, connection_str, quora_db):
        self.client = pymongo.MongoClient(connection_str)
        self.db = self.client[quora_db]
        self.crawled_questions = {}
        self.bad_questions = set()

    def crawl_by_question(self, question):
        # Not crawling the question that was already crawled
        if question in self.crawled_questions or question in self.bad_questions:
            return

        print 'analyzing question: %s' % question
        question_stats = Quora.get_question_stats(question)

        # If something went awry crawling particular question
        if question_stats == {}:
            self.bad_questions.add(question)
            return

        latest_answers = Quora.get_latest_answers(question)
        question_stats['latest_answers'] = latest_answers

        print 'question_stats:\n', question_stats
        print 'latest_answers:\n', latest_answers
        print 'related_questions: \n', question_stats['related_questions']
        print '---------------------------------------------------'

        self.crawled_questions[question] = question_stats

        # Inserting into database as we go...
        self.db.questions.insert({question: question_stats})

        for related_question in question_stats['related_questions']:
            # Only considering complete questions (i.e. not ending in ...)
            if not related_question.endswith('...'):
                self.crawl_by_question(_sanitize_question(related_question))


