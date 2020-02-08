# -*- coding: utf-8 -*-

"""
连接会话模块
"""

from socket import socket, AF_INET, SOCK_STREAM
import json
import re


class Session():
    """
    用于与服务器连接的会话服务类
    """

    def __init__(self, ip, port, userid, password, encoding='utf-8'):
        """
        会话服务构造函数

        ip:
          服务器IP地址
        port:
          服务器端口
        userid:
          用户ID
        password:
          用户密码（密文）
        """
        self.ip = ip
        self.port = port
        self.userid = userid
        self.password = password
        self.url = '%s:%d' % (ip, port)
        self.socket = None
        self.sessionid = None
        self.cxcookie = None
        self.encoding = encoding

    def connect(self):
        """
        建立TCP连接
        """
        self.disconnect()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

    def disconnect(self):
        """
        断开TCP连接
        """
        if self.socket:
            self.socket.close()
            self.socket = None

    def read_line(self):
        """
        读入一行字符串数据（不包含回车换行）
        """
        l, c, p = b'', b'', b''
        while True:
            c = self.socket.recv(1)
            if p == b'\x0d' and c == b'\x0a':
                return l[0:-1].decode(self.encoding)
            l += c
            p = c

    def read_data(self, blen):
        """
        按指定长度'blen'读入数据，返回(读入长度,读入字符串)
        """
        rec = self.socket.recv(blen)
        return len(rec), rec

    def read_header(self):
        """
        读入传输数据协议头
        """
        result = ''
        while True:
            line = self.read_line()
            if not line:
                break
            result += line + '\n'
        return result

    def read_body(self, header=None, debug=False):
        """
        读入传输数据协议内容
        """
        data = b''
        if not header:
            header = self.read_header()
        if re.search('Transfer-Encoding: chunked', header):
            while True:
                blen = self.read_line()
                blen = int(blen, 16)
                if blen <= 0:
                    self.read_line()
                    break
                while True:
                    rlen, rec = self.read_data(blen)
                    data += rec
                    blen -= rlen
                    if blen <= 0:
                        break
                self.read_line()
        else:
            # TODO: 其它传递形式，目前尚未发现
            pass
        result = data.decode(self.encoding)
        if debug:
            print("READ: %s\n\n" % result)
        return result

    def make_post_content(self, content):
        """
        构建提交服务器的文本内容
        """
        result = "POST /hncjb/reports/crud HTTP/1.1\n" \
                 "Host: {url}\n" \
                 "Connection: keep-alive\n" \
                 "Content-Length: {content_size}\n" \
                 "Accept: application/json, text/javascript, */*; q=0.01\n" \
                 "Origin: http://{url}\n" \
                 "X-Requested-With: XMLHttpRequest\n" \
                 "User-Agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\n" \
                 "Content-Type: multipart/form-data;charset=UTF-8\n" \
                 "Referer: http://{url}/hncjb/pages/html/index.html\n" \
                 "Accept-Encoding: gzip, deflate\n" \
                 "Accept-Language: zh-CN,zh;q=0.8\n"
        result = result.format(url=self.url,
                               content_size=len(content.encode(self.encoding)))
        if self.sessionid:
            result += "Cookie: jsessionid_ylzcbp={}; cxcookie={}\n".format(
                self.sessionid, self.cxcookie)
        result += "\n" + content
        return result

    def make_service_content(self, serviceid, params, debug):
        """
        构建提交服务器的文本内容的模板方法
        """
        result = '{{"serviceid":"{serviceid}","target":"","sessionid":null,' \
                 '"loginname":"{userid}","password":"{password}",' \
                 '"params":{{{params}}},"datas":[{{{params}}}]}}'
        result = result.format(serviceid=serviceid, params=params,
                               userid=self.userid, password=self.password)
        if debug:
            print('POST: %s\nDATA: %s\n\n' % (serviceid, result))
        return result

    def post(self, service_content):
        self.socket.send(self.make_post_content(
            service_content).encode('utf-8'))

    def post_service_content(self, serviceid, params, debug=False):
        self.post(self.make_service_content(serviceid, params, debug))

    def parse(self, jsonsrc):
        return json.loads(jsonsrc)

    def login(self):
        """
        递交登陆信息
        """
        service_content = '{"serviceid":"loadCurrentUser","target":"","sessionid":null,' \
                          '"loginname":null,"password":null,"params":{},"datas":[{}]}'
        self.post(service_content)
        header = self.read_header()
        m = re.search('Set-Cookie: jsessionid_ylzcbp=(.+?);', header)
        if m:
            self.sessionid = m.group(1)
        m = re.search('Set-Cookie: cxcookie=(.+?);', header)
        if m:
            self.cxcookie = m.group(1)
        self.parse(self.read_body(header))

        service_content = '{{"serviceid":"syslogin","target":"","sessionid":null,' \
                          '"loginname":null,"password":null,' \
                          '"params":{{"username":"{userid}","passwd":"{password}"}},' \
                          '"datas":[{{"username":"{userid}","passwd":"{password}"}}]}}'
        self.post(service_content.format(
            userid=self.userid, password=self.password))
        return self.parse(self.read_body())

    def logout(self):
        """
        递交退出信息
        """
        self.post_service_content('syslogout', '')

    def zhcxgrinfo_query(self, idcard, xzqh='', cjbm='', cbzt='', jfzt='', sort='', pageno=1, pagesize=15):
        """
        综合查询个人信息
        """
        # aac002 身份证号码 aac003 姓名
        # aac008 参保状态: "1"-正常参保 "2"-暂停参保 "4"-终止参保 "0"-未参保
        # aac031 缴费状态: "1"-参保缴费 "2"-暂停缴费 "3"-终止缴费
        # aac066 参保身份: "011"-普通参保 "021"-残疾一级 "022"-残疾二级 "031"-"特困一级"
        params = '"aaf013":"{xzqh}","aaz070":"{cjbm}","aaf101":"","aac009":"","aac008":"{cbzt}",' \
                 '"aac031":"{jfzt}","aac006str":"","aac006end":"","aac066":"","aae030str":"",' \
                 '"aae030end":"","aae476":"","aac003":"","aac002":"{idcard}",' \
                 '"page":{pageno},"pagesize":{pagesize},"filtering":[],"sorting":[{sort}],"totals":[]'
        self.post_service_content('zhcxgrinfoQuery', params.format(**locals()))
        return self.parse(self.read_body())

    def jfxxcx_queryjfxx(self, idcard, qsjfsj, jzjfsj, jfnd='', xz='', cun=''):
        """
        缴费信息查询
        """
        params = '"xz":"{xz}","cun":"{cun}","aac002":"{idcard}","aac003":"","aae0031":"{qsjfsj}",' \
                 '"aae0032":"{jzjfsj}","aac009":"","aaz288":"","aae0061":"","aae0062":"",' \
                 '"aae167":"001","aab033":"","bie013":"","aae003":"{jfnd}","aac066":"","aae1741":"",' \
                 '"aae1742":"","aac031":"","yesno":"1","page":1,"pagesize":15,"filtering":[],' \
                 '"sorting":[],"totals":[]'
        self.post_service_content(
            'jfxxcx_queryjfxx', params.format(**locals()))
        return self.parse(self.read_body())

    def cbzzfh_perinfo_list(self, idcard, pageno=1, pagesize=10):
        """
        参保终止复核人员列表
        """
        params = '"aaf013":"","aaf030":"","aae016":"","aae011":"","aae036":"",' \
                 '"aae036s":"","aae014":"","aae015":"","aae015s":"","aac002":"{idcard}",' \
                 '"aac003":"","aac009":"","aae160":"","page":{pageno},"pagesize":{pagesize},' \
                 '"filtering":[],"sorting":[],"totals":[]'
        self.post_service_content(
            "cbzzfhPerInfoList", params.format(**locals()))
        return self.parse(self.read_body())

    def cbzzfh_perinfo(self, js):
        """
        参保终止复核人员信息
        """
        params = '"aaz038":"{js[aaz038]}","aac001":"{js[aac001]}",' \
                 '"aae160":"{js[aae160]}"'
        self.post_service_content("cbzzfhPerinfo", params.format(**locals()))
        return self.parse(self.read_body())

    def dyzzfh_perinfo_list(self, idcard, pageno=1, pagesize=10):
        """
        待遇终止复核人员列表
        """
        params = '"aaf013":"","aaf030":"","aae016":"","aae011":"","aae036":"",' \
                 '"aae036s":"","aae014":"","aae015":"","aae015s":"","aac002":"{idcard}",' \
                 '"aac003":"","aac009":"","aae160":"","aic301":"","page":{pageno},' \
                 '"pagesize":{pagesize},"filtering":[],"sorting":[],"totals":[]'
        self.post_service_content(
            "dyzzfhPerInfoList", params.format(**locals()))
        return self.parse(self.read_body())

    def dyzzfh_perinfo(self, js):
        """
        待遇终止复核人员信息
        """
        params = '"aaz176":"{js[aaz176]}"'
        self.post_service_content("dyzzfhPerinfo", params.format(**locals()))
        return self.parse(self.read_body())

    def get_zzyy_cn(self, zzyy):
        """
        获得终止原因中文名
        """
        return {"1401": "死亡", "1406": "出外定居", "1407": "参加职保",
                "1499": "其他原因", "6401": "死亡", "6406": "出外定居",
                "6407": "参加职保", "6499": "其他原因"}[zzyy]

    def sngxzcfh_perinfo_list(self, idcard, pageno=1, pagesize=10):
        """
        省内制度衔接转出复核人员列表
        """
        params = '"aaf013":"","aaf030":"","aae016":"","aae011":"","aae036":"",' \
                 '"aae036s":"","aae014":"","aae015":"","aae015s":"","aac002":"{idcard}",' \
                 '"aac003":"","aac009":"","xzbz":"1","page":{pageno},"pagesize":{pagesize},' \
                 '"filtering":[],"sorting":[],"totals":[]'
        self.post_service_content(
            "sngxzcfhPerInfoList", params.format(**locals()))
        return self.parse(self.read_body())

    def sngxzcfh_perinfo(self, js):
        """
        省内制度衔接转出复核人员信息
        """
        params = '"aaz160":"{js[aaz160]}"'
        self.post_service_content("sngxzcfhPerinfo", params.format(**locals()))
        return self.parse(self.read_body())

    def query_zzfh_info(self, idcard):
        """
        查询终止复核信息
        """
        fhlx = ''  # 终止复核类型
        fhyy = ''  # 终止复核原因
        zzsj = ''  # 终止时间
        fhsj = ''  # 复核时间
        memo = ''  # 备注

        infos = self.cbzzfh_perinfo_list(idcard)
        if infos and infos['rowcount'] > 0:
            info = self.cbzzfh_perinfo(infos['datas'][0])['datas'][0]
            fhlx = '参保终止'
            fhyy = self.get_zzyy_cn(info['aae160'])
            zzsj = info['aae031']
            fhsj = info['aae036'].replace("-", "").split(" ")[0]
            memo = info['aae013']
        else:
            infos = self.dyzzfh_perinfo_list(idcard)
            if infos and infos['rowcount'] > 0:
                info = self.dyzzfh_perinfo(infos['datas'][0])['datas'][0]
                fhlx = '待遇终止'
                fhyy = self.get_zzyy_cn(info['aae160'])
                zzsj = info['aic301']
                fhsj = info['aae036'].replace("-", "").split(" ")[0]
                memo = info['aae013']
            else:
                infos = self.sngxzcfh_perinfo_list(idcard)
                if infos and infos['rowcount'] > 0:
                    info = self.sngxzcfh_perinfo(infos['datas'][0])['datas'][0]
                    fhlx = "制度衔接"
                    fhyy = "转入职保"
                    zzsj = info['aae035']
                    fhsj = info['aae036'].replace("-", "").split(" ")[0]
                    memo = info['aae013']
        return fhlx, fhyy, zzsj, fhsj, memo


class DefaultSession:
    def __init__(self, sessioncls=Session):
        if not issubclass(sessioncls, Session):
            raise Exception('%r is not a subclass of %r',
                            sessioncls.__name__, Session.__name__)
        self.__session = sessioncls("10.136.6.99", 7010, "430302002",
                                    "72fb9d9c611b751ddeaefdedda7a557b")

    def __enter__(self):
        self.__session.connect()
        self.__session.login()
        return self.__session

    def __exit__(self, e_t, e_v, t_b):
        self.__session.logout()
        self.__session.disconnect()


if __name__ == '__main__':
    with DefaultSession() as session:
        # print(session.zhcxgrinfo_query('430302196301125023'))#'430303193409290023'))
        #print(session.jfxxcx_queryjfxx('430321195607160512', '20160101', '20160831'))
        print(session.query_zzfh_info('430321195610140512'))
