#!/usr/bin/env python

from crawler import Crawler


def main():
    # You can provide whatever query you like e.g. 'Barrack Obama', 'isis', 'mongodb'
    # example_query = 'isis'


    # Searching for 'isis' keyword and getting relevant snippets related to this keyword.
    # search_results_snippets = Quora.get_snippets_by_query(example_query)

    # Saving list of snippets obtained by query: 'isis' under 'snippets' collection in 'quora' db
    # db.snippets.insert({example_query: search_results_snippets})

    connection_str = 'mongodb://localhost:27017/'
    quora_db = 'quora'

    # Creating crawler object with limited crawling depth
    crawler = Crawler(connection_str, quora_db, maxdepth=3)
    seed = 'What-is-terrorism'
    # Starting crawling
    crawler.crawl_by_question(seed)

if __name__ == '__main__':
    main()