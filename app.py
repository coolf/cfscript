# -*- coding: UTF-8 -*-
import random,requests,time
import re
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
class loginQQ():
    def getcode():
        sourceURL = 'http://find.qq.com/index.html?version=1&im_version=5533&width=910&height=610&search_target=0'
        s=requests.session()

        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.59 QQ/8.9.3.21169 Safari/537.36'
                }
        s.headers.update(headers)
        url = 'http://ui.ptlogin2.qq.com/cgi-bin/login'
        params = {
            'appid': '21000124',
            'daid': '73',
            'pt_no_auth': '1',
            's_url': sourceURL
        }
        r = s.get(url, params=params, timeout=1000)
        cookies=r.cookies.get_dict()
        login_sig=cookies['pt_login_sig']
        url='https://ssl.ptlogin2.qq.com/ptqrshow?appid=21000124&e=2&l=M&s=3&d=72&v=4&t=0.8386%d&daid=8&pt_3rd_aid=0'%int(random.uniform(10000,99999))
        r=s.get(url,headers=headers)
        with open('login.png','wb') as f:
            f.write(r.content)

    cookies=r.cookies.get_dict()
    qrsig=cookies['qrsig']
    ptqrtoken=genqrtoken(qrsig)
    print(cookies)
    while True:
        # url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=http%3A%2F%cf.qq.com&ptqrtoken=' + ptqrtoken + '&ptredirect=0&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-1534141126141&js_ver=10278&js_type=1&login_sig=' + login_sig + '&pt_uistyle=40&aid=21000124&daid=164&mibao_css=m_webqq&'
        url='https://ssl.ptlogin2.qq.com/ptqrlogin?u1=http%3A%2F%2Fcf.qq.com%2F&ptqrtoken='+ptqrtoken+'&ptredirect=1&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-1534166624243&js_ver=10278&js_type=1&login_sig=&pt_uistyle=40&aid=21000124&daid=8&'
        r = s.get(url, cookies=cookies, headers=headers).text
        print(r)
        time.sleep(1)
        if '登录成功' in r:
            break
    url=r.split(',')[2][1:-1]
    print(url)
    r=s.get(url,headers=headers,allow_redirects=False)
    print(r.text)
    j_cookie=r.cookies.get_dict()
    print(j_cookie)

 #获取个人资料
# s.headers.update({'Referer': 'http://s.web2.qq.com/proxy.html'})
# r=s.get('http://s.web2.qq.com/api/get_self_info2?t=%d'%int(time.time()*1000),headers=headers,cookies=j_cookie)
# print(r.json())
# print(r.cookies.get_dict())
#

#  查战绩
# url='http://apps.game.qq.com/cgi-bin/cf/userinfo/userinfo.cgi?ssn=354'
# gtk = genbkn(j_cookie['skey'])
# print('gtk',gtk)
# r=s.get(url,headers=headers,cookies=j_cookie)
# r.encoding='gb2312'
# print(r.text)


url='http://cf.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=cf&iActivityId=152535&sServiceDepartment=group_f&sSDID=f2f146ceab460522dd63ad61f7745df8&isXhrPost=true'
# url='http://cf.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=cf&iActivityId=153469&sServiceDepartment=group_f&sSDID=f2f146ceab460522dd63ad61f7745df8&isXhrPost=true'
data={
    'ameVersion': 0.3,
    'sServiceType': 'cf',
    'iActivityId': '152535',
    'sServiceDepartment': 'group_f',
    'sSDID': 'f2f146ceab460522dd63ad61f7745df8',
    'isXhrPost': 'true',
    'gameId':'',
    'sArea':'',
    'iSex':'',
    'sRoleId':'',
    'iGender':'',
    'xhr': 1,
    'id':1,
    'sServiceType': 'cf',
    'objCustomMsg':'',
    'areaname':'',
    'roleid':'',
    'rolelevel':'',
    'rolename':'',
    'areaid':'',
    'iActivityId': 152535,
    'iFlowId': 477478,
    'g_tk': gtk,
    'e_code': 0,
    'g_code': 0,
    'eas_url': 'http%3A%2F%2Fcf.qq.com%2Fcp%2Fa20180719recall%2F',
    'eas_refer':'http%3A%2F%2Fcf.qq.com%2F',
    'sServiceDepartment': 'group_f',
    'xhrPostKey': 'xhr_1534167746143'
}

r=s.post(url,data=data,headers=headers,cookies=j_cookie)
print(r.json())

