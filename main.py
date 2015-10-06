#!/usr/bin/env python

import pymongo
from quora import Quora

def main():
    connection_str = 'mongodb://localhost:27017/'
    quora_db = 'quora'

    # You can provide whatever query you like e.g. 'Barrack Obama', 'isis', 'mongodb'
    example_query = 'isis'

    client = pymongo.MongoClient(connection_str)
    db = client[quora_db]

    # Searching for 'isis' keyword and getting relevant snippets related to this keyword.
    search_results_snippets = Quora.get_snippets_by_query(example_query)

    # Saving list of snippets obtained by query: 'isis' under 'snippets' collection in 'quora' db
    db.snippets.insert({example_query: search_results_snippets})

if __name__ == '__main__':
    main()