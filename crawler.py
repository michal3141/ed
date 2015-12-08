import pymongo
from pyquora.quora import Quora, User
from utils import _sanitize_username, _sanitize_question
from explorer import _get_question

__author__ = 'michal3141'


class Crawler(object):
    def __init__(self, connection_str, quora_db, maxdepth=1):
        """
        :param connection_str: Connection string to Mongo database
        :param quora_db: Name of DB used to store crawled data
        :param maxdepth: Limiting depth for crawler, 1 - crawling only seed, 2 - crawling seed and related objects, etc.
        :return:
        """
        self.client = pymongo.MongoClient(connection_str)
        self.db = self.client[quora_db]
        self.maxdepth = maxdepth
        self.crawled_questions = {}
        self.crawled_users = {}
        self.bad_questions = set()
        self.bad_users = set()

    def crawl_by_user(self, user):
        self._crawl_by_user(user, 1)

    def _crawl_by_user(self, user, depth):
        # Stopping crawling when depth exceeds maxdepth
        if depth > self.maxdepth:
            return

        if user in self.crawled_users or user in self.bad_users:
            return

        print 'crawling user: %s' % user

        user_stats = User.get_user_stats(user, followers=True, following=True)

        # If something went awry crawling particular user
        if user_stats == {}:
            self.bad_users.add(user)
            return

        print 'user_stats:\n', user_stats
        print '---------------------------------------------------'

        self.crawled_users[user] = user_stats

        # Inserting into database as we go...
        self.db.users.insert({user: user_stats})

        for related_user in user_stats['following'] + user_stats['followers']:
                self._crawl_by_user(_sanitize_username(related_user), depth+1)

    def crawl_by_question(self, question):
        self._crawl_by_question(question, 1)

    def _crawl_by_question(self, question, depth):
        # Stopping crawling when depth exceeds maxdepth
        if depth > self.maxdepth:
            return

        # Not crawling the question that was already crawled
        if question in self.crawled_questions or question in self.bad_questions:
            return

        print 'crawling question: %s' % question
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
                self._crawl_by_question(_sanitize_question(related_question), depth+1)

    def crawl_questions_and_answers(self):
        ## This is for downloading - uncomment if you want to download ##
        # questions_data = list(self.db.questions.find())
        # for document in questions_data:
        #     question = _get_question(document)
        #     print question
        #     question_author, answers_authors = Quora.get_authors_of_questions_and_answers(question)
        #     question_author = _sanitize_username(question_author)
        #     answers_authors = [_sanitize_username(author) for author in answers_authors] 
        #     stats = {'question_author' : question_author, 'answers_authors': answers_authors}
        #     print 'question_author:', question_author
        #     print 'answers_authors:', answers_authors

        #     # Inserting into database:
        #     self.db.answers.insert({question: stats})

        ## This is purely for updating ##
        answers_data = list(self.db.answers.find())
        for document in answers_data:
            question = _get_question(document)

            if document[question]['question_author'] == '':
                print question
                print document['_id']

                question_author, answers_authors = Quora.get_authors_of_questions_and_answers(question)
                
                question_author = _sanitize_username(question_author)
                answers_authors = [_sanitize_username(author) for author in answers_authors]

                print 'question_author:', question_author
                print 'answers_authors:', answers_authors
                stats = {'question_author' : question_author, 'answers_authors': answers_authors}
                self.db.answers.update({'_id':document['_id']}, {"$set": {question: stats}}, upsert=False)

            else:
                question_author = document[question]['question_author']
                answers_authors = document[question]['answers_authors']

                question_author = _sanitize_username(question_author)
                answers_authors = [_sanitize_username(author) for author in answers_authors]

                stats = {'question_author' : question_author, 'answers_authors': answers_authors}
                self.db.answers.update({'_id':document['_id']}, {"$set": {question: stats}}, upsert=False)