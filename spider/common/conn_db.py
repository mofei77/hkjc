
from pymongo import MongoClient

class myMongoClient():
    def __init__(self,host=None,db=None):
        self.host = host
        self.db = MongoClient(self.host)[db]


server = 'mongodb://mofei:kingmofei@107.167.177.248:27017/'
local = 'mongodb://localhost:27017/'

mongodb = myMongoClient(local,'hkjc')

if __name__ == '__main__':

    db = mongodb.db['sports']
    rtype = {'jsontype': 'league','tournamentID':'1644'}
    print(list(db.find(rtype)))