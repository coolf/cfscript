from pymongo import *
from bson import ObjectId
import requests,json
client = MongoClient('119.28.41.142', 25412)
db = client.cf

def insert(url,name,sSDID,iActivityId,iFlowId,dtEndTime):
    data = {
        'url':url,
        'dtEndTime':dtEndTime,
        'name': name,
        'sSDID': sSDID,
        'iActivityId': iActivityId,
        'iFlowId': iFlowId
    }
    print(db.content.insert(data))
def qwbzj(req, x, y):
    a = req.find(x)
    b = req.find(y, int(a + 1))
    return req[a + len(x):b]
def getInfo(url):

    r=requests.get(url)
    r.encoding='gbk'
    uid=qwbzj(r.text,'//ossweb-img.qq.com/images/ams/atm/reporting.js?action=','"></script>')
    name=qwbzj(r.text,'<title>','</title>').replace('穿越火线官方网站','').replace('腾讯游戏','').replace('-','')
    print(uid,name)
    urls='http://cf.qq.com/comm-htdocs/js/ams/actDesc/'+uid[3:]+'/'+uid+'/act.desc.js'
    r=requests.get(urls).text
    print(urls)
    print(r)
    content=qwbzj(r,'var ams_actdesc=','var')
    # print(content)
    content=json.loads(content)
    iActivityId=content['iActivityId']
    sSDID=content['sSDID']
    dtEndTime=content['dtEndTime']
    iFlowId=content['flows']
    iFlowIds=[]
    for x in iFlowId:
        iFlowIds.append(x[2:])
        # print(x[2:])
    # print(name, sSDID, iActivityId, iFlowIds, dtEndTime,url)
    insert(name=name, sSDID=sSDID, iActivityId=iActivityId, iFlowId=iFlowIds, dtEndTime=dtEndTime,url=url)
if __name__=='__main__':
    getInfo(url='https://cf.qq.com/cp/a20180807nzxynew/index.htm')