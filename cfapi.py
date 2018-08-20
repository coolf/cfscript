import random, requests, time, json, base64
import re, os
from flask_cors import *
from flask import Flask, request, session, make_response, jsonify, url_for, redirect
from urllib.parse import quote, unquote, urlencode
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_socketio import SocketIO, emit

app = Flask(__name__)

CORS(app, supports_credentials=True)
app.secret_key = '254127401'
app.config.update(
    MONGO_URI='mongodb://119.28.41.142:25412/cf',
)
socketio = SocketIO(app)
mongo = PyMongo(app)


#  计算 qrsig
def genqrtoken(qrsig):
    e = 0
    for i in range(0, len(qrsig)):
        e += (e << 5) + ord(qrsig[i])
    qrtoken = (e & 2147483647)
    return str(qrtoken)
    #  计算bkn


def genbkn(skey):
    b = 5381
    for i in range(0, len(skey)):
        b += (b << 5) + ord(skey[i])
    bkn = (b & 2147483647)
    return str(bkn)
    #  计算 Hash


def getHashCode(b, j):
    a = [0, 0, 0, 0]
    for i in range(0, len(j)):
        a[i % 4] ^= ord(j[i])

    w = ["EC", "OK"]
    d = [0, 0, 0, 0]

    d[0] = int(b) >> 24 & 255 ^ ord(w[0][0])
    d[1] = int(b) >> 16 & 255 ^ ord(w[0][1])
    d[2] = int(b) >> 8 & 255 ^ ord(w[1][0])
    d[3] = int(b) & 255 ^ ord(w[1][1])

    w = [0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(0, 8):
        if i % 2 == 0:
            w[i] = a[i >> 1]
        else:
            w[i] = d[i >> 1]
    a = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    d = ""

    for i in range(0, len(w)):
        d += a[w[i] >> 4 & 15]
        d += a[w[i] & 15]

    return d


def qwbzj(req, x, y):
    a = req.find(x)
    b = req.find(y, int(a + 1))
    return req[a + len(x):b]


class loginQQ(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.59 QQ/8.9.3.21169 Safari/537.36'
    }
    s = requests
    Dcode = {}

    # # 大区代码
    def getDcode(self):
        CFcode = requests.get('http://cf.qq.com/cp/a20170210information/js/userindexinfo.js').text
        CFcode = qwbzj(CFcode, 'var AREANAMEDATA = ', ';').replace('{', '').replace('}', '').replace("'",
                                                                                                     '').strip().split(
            ',')
        for x in CFcode:
            x = x.strip().split(' : ')
            self.Dcode[x[0]] = x[1]

    def getQRCode(self):
        R_cookie = {}
        sourceURL = 'http://find.qq.com/index.html?version=1&im_version=5533&width=910&height=610&search_target=0'
        self.headers.update(self.headers)
        url = 'http://ui.ptlogin2.qq.com/cgi-bin/login'
        params = {
            'appid': '21000124',
            'daid': '73',
            'pt_no_auth': '1',
            's_url': sourceURL
        }
        r = self.s.get(url, params=params, timeout=1000)
        cookies = r.cookies.get_dict()
        # print(cookies)
        for cookie in cookies:
            R_cookie[cookie] = cookies[cookie]
        login_sig = cookies['pt_login_sig']
        url = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=21000124&e=2&l=M&s=3&d=72&v=4&t=0.8386%d&daid=8&pt_3rd_aid=0' % int(
            random.uniform(10000, 99999))
        r = self.s.get(url, headers=self.headers)
        cookies = r.cookies.get_dict()
        for cookie in cookies:
            R_cookie[cookie] = cookies[cookie]
        # 唯一二维码
        qrcodePath = login_sig + 'qq.png'
        with open(qrcodePath, 'wb') as f:
            f.write(r.content)
        url = 'http://pic.sogou.com/pic/upload_pic.jsp'
        files = {'file': ('qrcode', open(qrcodePath, 'rb'), 'image/png')}
        r = requests.post(url, data=None, files=files).text
        os.remove(qrcodePath)
        res = make_response(jsonify({'code': '200', 'data': r}))
        for x in R_cookie:
            res.set_cookie(x, R_cookie[x])
        return res

    def qrLogin(self):
        qrsig = request.cookies.get('qrsig')
        ptqrtoken = genqrtoken(qrsig)
        # url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=http%3A%2F%cf.qq.com&ptqrtoken=' + ptqrtoken + '&ptredirect=0&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-1534141126141&js_ver=10278&js_type=1&login_sig=' + login_sig + '&pt_uistyle=40&aid=21000124&daid=164&mibao_css=m_webqq&'
        url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=http%3A%2F%2Fcf.qq.com%2F&ptqrtoken=' + ptqrtoken + '&ptredirect=1&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-1534166624243&js_ver=10278&js_type=1&login_sig=&pt_uistyle=40&aid=21000124&daid=8&'
        r = self.s.get(url, cookies=request.cookies, headers=self.headers).text
        if '登录成功' in r:
            url = r.split(',')[2][1:-1]
            print(url)
            r = self.s.get(url, headers=self.headers, allow_redirects=False)
            print(r.text)
            j_cookie = r.cookies.get_dict()
            res = make_response(jsonify({'code': '200', 'data': '登陆成功!'}))
            for cookie in j_cookie:
                res.set_cookie(cookie, j_cookie[cookie])
            return res
        if '二维码未失效' in r:
            r = '二维码未失效'
        elif '二维码认证中' in r:
            r = '二维码认证中'
        elif '登录成功' in r:
            r = '登录成功'
        elif '二维码已失效' in r:
            r = '二维码已失效'
        else:
            r = str(r)
        return jsonify({'code': 200, 'data': r})

    # 获取个人资料
    def user(self):
        if not 'skey' in request.cookies:
            return '未登陆！'
        else:
            D_id, areaid, level, qq = self.getDaqu()
            # hxbnum = self.getHxb()
            # cfnum = self.getCf()
            cfname = self.getName(D_id, qq)
            data = {
                'qq': qq,
                'areaid': areaid,
                'level': level,
                # 'hxbnum': hxbnum,
                # 'cfnum': cfnum,
                'cfname': cfname
            }
            res = make_response(jsonify({'code': 200, 'data': data}))
            for datas in data:
                res.set_cookie(datas, self.textEncode(data[datas], 1))
            return res

    # 获取大区信息
    def getDaqu(self):
        self.headers.update({'Referer': 'http://cf.qq.com'})
        gtk = genbkn(request.cookies.get('skey'))
        # url = 'http://apps.game.qq.com/wmp/v3.1/?p0=1&p1=searchUserInfo&p2=0&r0=script&r1=checkUserObj&openId=&agent=&channel=&area=&&gicp_tk='+gtk+'&_='
        url = 'http://apps.game.qq.com/cf/a20170210information/getCfUserInfo.php?rd=0.2005390673406151&_='
        r = self.s.get(url, headers=self.headers, cookies=request.cookies).text
        r = qwbzj(r, 'var getcfuserinfo_result = ', ';')
        r = json.loads(r)
        # 大区id
        D_id = r['jData']['areaid']
        areaid = self.Dcode[D_id]
        # 大区等级
        level = r['jData']['level']
        # 大区名字
        qq = request.cookies.get('uin')[1:]
        if qq[0] == '0':
            qq = qq[1:]
        return D_id, areaid, level, qq

    # 获取名字
    def getName(self, uid, qq):
        if request.cookies.get('cfname') == None:
            url = 'http://cf.aci.game.qq.com/main?game=cf&area=' + uid + '&callback=153431465494010943&sCloudApiName=ams.gameattr.role&iAmsActivityId=http%3A%2F%2Fcf.qq.com%2Fclan%2F'
            r = self.s.get(url, headers=self.headers, cookies=request.cookies).text
            # print(r)
            cfname = self.textEncode(qwbzj(r, qq, '|'), 0)
            return cfname
        else:
            return self.textEncode(request.cookies.get('cfname'), 0)

    # 获取火线币
    def getHxb(self):
        if request.cookies.get('hxbnum') == None:
            hxburl = 'http://apps.game.qq.com/cf/a20170210information/getCfHxbInfo.php?action=getMyHxbInfo&rd=0.8823276921287142&_='
            r = self.s.get(hxburl, headers=self.headers, cookies=request.cookies).text
            r = qwbzj(r, 'hxbinfo_result = ', ';')
            r = json.loads(r)
            return r['jData']['mp']
        else:
            return self.textEncode(request.cookies.get('hxbnum'), 0)

    # 获取CF点
    def getCf(self):
        if request.cookies.get('cfnum') == None:
            cfurl = 'http://apps.game.qq.com/cf/a20170210information/getCfcashInfo.php?action=getMycashInfo&rd=0.7396993943602372&_='
            r = self.s.get(cfurl, headers=self.headers, cookies=request.cookies).text
            r = qwbzj(r, 'cashinfo_result = ', ';')
            # print(r)
            r = json.loads(r)
            return r['jData']['cash']
        else:
            return self.textEncode(request.cookies.get('cfnum'), 0)

    # 获取个人仓库
    def getCfBagInfo(self):
        url = 'http://apps.game.qq.com/cf/a20170210information/getCfBagInfo.php?action=getMyBagInfo&rd=0.022023812851510005'
        r = self.s.get(url, headers=self.headers, cookies=request.cookies).text
        r = qwbzj(r, 'var getmybaginfo_result = ', ';')
        print(json.loads(r))
        return json.loads(r)

    def go(self, sSDID, iActivityId, iFlowId):
        gtk = genbkn(request.cookies.get('skey'))
        url = 'http://cf.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=cf&iActivityId=' + iActivityId + '&sServiceDepartment=group_f&sSDID=' + sSDID + '&isXhrPost=true'
        # url='http://cf.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=cf&iActivityId=153469&sServiceDepartment=group_f&sSDID=f2f146ceab460522dd63ad61f7745df8&isXhrPost=true'
        # url = 'http://cf.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=cf&iActivityId=156454&sServiceDepartment=group_f&sSDID=f6df697985491cf211775f1e8c492661&isXhrPost=true'
        data = {
            'ameVersion': 0.3,
            'sServiceType': 'cf',
            'iActivityId': iActivityId,
            'sServiceDepartment': 'group_f',
            'sSDID': sSDID,
            'isXhrPost': 'true',
            'gameId': '',
            'sArea': '',
            'iSex': '',
            'sRoleId': '',
            'iGender': '',
            'xhr': 1,
            'id': 1,
            'sServiceType': 'cf',
            'objCustomMsg': '',
            'areaname': '',
            'roleid': '',
            'rolelevel': '',
            'rolename': '',
            'areaid': '',
            'iActivityId': iActivityId,
            'iFlowId': iFlowId,
            'g_tk': gtk,
            'e_code': 0,
            'g_code': 0,
            'eas_url': 'http://cf.qq.com/',
            'eas_refer': 'http%3A%2F%2Fcf.qq.com%2F',
            'sServiceDepartment': 'group_f',
            'xhrPostKey': 'xhr_1534167746143'
        }

        r = self.s.post(url, data=data, headers=self.headers, cookies=request.cookies).json()
        return r['flowRet']['sMsg']

    def getShopInfo(self):
        id = list(self.Dcode.keys())[list(self.Dcode.values()).index(self.textEncode(request.cookies.get('areaid'), 0))]
        self.headers.update({'Referer': 'http://kf.qq.com/game/consume_records.html'})
        url = 'http://kf.qq.com/cgi-bin/common'
        params = {
            'rand': 0.05177981547634203,
            'command': 'command=C00006&fromtype=kfweb&fromtoolid=kfweb514&type=getCFSpend&area=' + id + '&server_id=103&server_name=&area_id=' + id + '&area_name='
        }
        r = self.s.get(url, params=params, headers=self.headers, cookies=request.cookies).json()
        if r['resultcode'] == 0:
            if len(r['resultinfo']['list'][0]) > 1:
                shopid = r['resultinfo']['list'][0]['list'].split('|')
                shopid = shopid[1:-1]
                return jsonify({'code': '200', 'nun': len(shopid), 'data': shopid})
            else:
                return jsonify({'code': '200', 'nun': 0, 'data': 0})
        else:
            return jsonify({'code': '200', 'data': '未登陆！'})

    def loginStatus(self):
        try:
            url = 'http://apps.game.qq.com/qlang/cf/recActivity/qlang/getArea.ql?service=cf&_='
            r = self.s.get(url, cookies=request.cookies, headers=self.headers).text
            # print(r)
            if r.find('Not Login') != -1:
                return False
            else:
                return True
        except Exception as e:
            print(e)

    def textEncode(self, text, code):
        if code == 1:
            return quote(text)
        elif code == 0:
            return unquote(text)

    # 获取活动
    def getIteam(self):
        a = mongo.db.content.find({}, {'name': '$name', 'iFlowId': '$iFlowId'})
        Tieam = []
        for x in a:
            print(a)
            name = {}
            name['name'] = x['name']
            name['num'] = len(x['iFlowId'])
            name['id'] = str(x['_id'])
            Tieam.append(name)
        return jsonify({'code': 200, 'data': Tieam})

    # 获取QQ所在城市
    def getQqCity(self, qq):
        url = 'http://yundong.qq.com/center/guest?_wv=2172899&asyncMode=1&uin=' + qq
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; PRO 6 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043221 Safari/537.36 V1_AND_SQ_7.0.0_676_YYB_D QQ/7.0.0.3135 NetType/WIFI WebP/0.3.0 Pixel/1080'})
        r = self.s.get(url, cookies=request.cookies, headers=self.headers).text
        return r


q = loginQQ()
q.getDcode()


# 获取二维码
@app.route('/')
def index():
    if q.loginStatus():
        return jsonify({'code': '201', 'data': '已登陆！'})
    else:
        imgpath = q.getQRCode()
        return imgpath


# 检测状态
@app.route('/login', methods=['GET'])
def login():
    if q.loginStatus():
        return jsonify({'code': '201', 'data': '已登陆！'})
    else:
        return q.qrLogin()


@app.route('/qq')
def qqCity():
    qq = request.args.get('qq')
    return q.getQqCity(qq)


@app.route('/go')
def go():
    id = request.args.get('id')
    idNum = request.args.get('idNum')
    return q.go(id, idNum)


# 注销

@app.route('/logout')
def logout():
    res = make_response(jsonify({'data': {'code': '200', 'data': True}}))
    for x in request.cookies.keys():
        res.delete_cookie(x)
    return res


# 获取用户信息
@app.route('/user')
def user():
    if q.loginStatus():
        return q.user()
    else:
        return jsonify({'code': 400, 'data': q.loginStatus()})


@app.route('/getcfbaginfo')
def getCfBagInfo():
    return jsonify({'data': q.getCfBagInfo()})


@app.route('/getShopInfo')
def getShopInfo():
    return q.getShopInfo()


@app.route('/getIteam')
def getIteam():
    return q.getIteam()


@socketio.on('connect', namespace='/getgo')
def handle_request2():
    print('=======================connect==========')

# @socketio.on('disconnect', namespace='/getgo')
# def disconnect(sid):
#     print('disconnect ')


@socketio.on('event', namespace='/getgo')
# def handle_request(request):
#     if request.get('data')=='初夏最牛逼':
#         a = mongo.db.content.find()
#         for x in a:
#             for num in x['iFlowId']:
#                 print(request,'==========================')
#                 status=q.go(x['sSDID'],x['iActivityId'],num)
#                 emit('response',{'data':status,'name':x['name'],'date':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) },broadcast=True)
#         emit('response',{'data':'领取完毕！','name':x['name'],'date':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
#     else:
#         emit('response','错误')
def handle_request(request):
    if request.get('data') == '初夏最牛逼':
        # 物品ID
        uid = int(request.get('uid'))
        # 请求的活动ID
        sid = int(request.get('sid'))
        # 获取活动数
        activity = mongo.db.content.find()
        # 活动ID
        aid = activity.count()
        if aid > sid and len(activity[sid]['iFlowId']) > uid:
            try:
                status = q.go(iFlowId=activity[sid]['iFlowId'][uid], sSDID=activity[sid]['sSDID'],
                              iActivityId=activity[sid]['iActivityId'])
                uid = uid +1 if len(activity[sid]['iFlowId']) > uid + 1 else 0
                if uid == 0:
                    emit('response', {'data': status, 'name': activity[sid]['name'], 'uid': uid, 'sid': sid+1,
                                      'date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                      'url': activity[sid]['url']})
                else:
                    emit('response', {'data': status, 'name':activity[sid]['name'],'uid': uid, 'sid': sid,'date':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'url':activity[sid]['url']})
                # emit('response','123')
            except Exception as e:
                print(e)
        else:
                emit('response', {'data': '领取完毕！', 'name':'领取完毕！', 'uid': -1, 'sid': -1,
                                  'date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                  'url': ''})
    #     if sid == 0 and uid == 0:
    #
    #     for x in a:
    #         if uid == 0:
    #             print(x)
    #             status = q.go(x['sSDID'], x['iActivityId'], x['iFlowId'][uid])
    #             print(status)
    #             uid = uid + 1 if len(x['iFlowId']) >= uid + 1 else False
    #             print(uid)
    #             emit('response',{'data': status, 'uid': uid, 'sid': str(x['_id'])})
    #         else:
    #             pass
    # else:
    #     emit('response', '错误')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
