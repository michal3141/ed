# ed
Data exploration

Project for studies. Analysis some data from Internet.
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

