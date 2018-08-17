from pymongo import *
from bson import ObjectId
client = MongoClient('119.28.41.142', 25412)
db = client.cf

data={
    'name':'幽灵爆破 领爆炸福利',
    'sSDID':'5500451c9594ac5821c137c097f5682b',
    'iActivityId':'152535',
    'iFlowId':['477478','477478','477478','477478','477478','477479','477479','477815','477489','477487','477472']
}
print(db.content.insert(data))





# a=db.content.find({},{'name':'$name','iFlowId':'$iFlowId','_id':'$_id'})
# Tieam=[]
# for x in a:
#     name = {}
#     a=str(x['_id'])
#     print(a)
#     name['name']=x['name']
#     name['num']=len(x['iFlowId'])
#     name['id']=a
#     Tieam.append(name)
# print(Tieam)