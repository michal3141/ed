import requests
from bs4 import BeautifulSoup

class Quora(object):
    quora_base_url = 'https://www.quora.com/'

    ## The user_agent is used to circumvent some script scrapping detection on quora side:
    ##      The server is currently unavailable. Please try again at a later time.
    ##      Our automated scripts have detected a possible scraper. If you feel we have made an err
    ## See more at: https://github.com/csu/pyquora/issues/74 (Setting 'User-agent' like below seems works fine)
    user_agent = {
        'User-agent': ' Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0',
    }

    @staticmethod
    def _get(url):
        return requests.get(url, headers = Quora.user_agent)

    @staticmethod
    def get_snippets_by_query(query):
        """Obtains snippets returned by the search

        :param query: Query for quora search e.g. 'isis'
        :type query: str.
        :returns:  list<str> - the list of snippets found for particular query.
        """
        url = Quora.quora_base_url + 'search?q=%s' % query
        
        soup = BeautifulSoup(Quora._get(url).text)

        # Getting text snippets from 'search_result_snippet' span
        search_result_snippets = [snippet.text for snippet in soup.find_all(
            'span', 
            attrs={'class' : 'search_result_snippet'}
        )]

        return search_result_snippets