# ed
Data exploration

Project for studies. Analysis for some data from quora.com.
Proposed technology stack: Python + MongoDB

Installing MongoDB on Ubuntu 14.04 LTS:
http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/

(27017 is the default listen port for mongod)

    michal3141@ubuntuu:~/studia/ed$ mongod --version
    db version v3.0.6
    git version: 1ef45a23a4c5e3480ac919b28afcba3c615488f2
    
Installing PyMongo Python driver:

    michal3141@ubuntuu:~/studia/ed$ sudo pip install pymongo
    michal3141@ubuntuu:~/studia/ed$ sudo pip freeze | grep -i mongo
    pymongo==3.0.3

Installing BeautifulSoup4 Python HTML parser:

    michal3141@ubuntuu:~/studia/ed$ sudo pip install BeautifulSoup4
    michal3141@ubuntuu:~/studia/ed$ sudo pip freeze | grep -i Beautiful
    beautifulsoup4==4.4.1

Installing feedparser:

    michal3141@ubuntuu:~/studia/ed$ sudo pip install feedparser
    michal3141@ubuntuu:~/studia/ed$ sudo pip freeze | grep feedparser
    feedparser==5.2.1

Installing selenium and deps (use: http://chromedriver.storage.googleapis.com/2.19/chromedriver_linux64.zip for chromedriver !). More:

    http://christopher.su/2015/selenium-chromedriver-ubuntu/
    
