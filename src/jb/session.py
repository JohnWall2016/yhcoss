from typing import *
from ..base.httpsocket import HttpSocket, HttpRequest
import re
from .jb_internal import session_conf as conf
from dataclasses import dataclass
from ..base.jsonable import Jsonable, jfield


# def dataclass(cls=None, *, id=''):
#
#    def wrap(cls):
#        cls = _dataclass(cls)
#        cls.service_id = id
#        return cls
#
#    if cls is None:
#        return wrap
#    return wrap(cls)


@dataclass
class Page:
    page: int = 1
    pagesize: int = 15
    filtering: List[Dict[str, str]] = jfield(default_factory=list)
    sorting: List[Dict[str, str]] = jfield(default_factory=list)
    totals: List[Dict[str, str]] = jfield(default_factory=list)


@dataclass
class Params:
    def __init__(self, service_id: str):
        self.service_id = service_id


def params(cls=None, *, id: str = ''):
    def wrap(cls):
        cls.service_id = id
        return cls

    if cls is None:
        return wrap
    return wrap(cls)


@dataclass
class Service(Jsonable):
    serviceid: str = ''
    target: str = ''
    sessionid: Optional[str] = None
    loginname: str = ''
    password: str = ''
    params: Optional[Any] = None
    datas: Optional[List[Any]] = None

    @staticmethod
    def new(params: Any, user_id: str, password: str):
        return Service(
            serviceid=params.service_id,
            loginname=user_id,
            password=password,
            params=params,
            datas=[params])


T = TypeVar('T')
U = TypeVar('U', bound='Result')


class Result(Protocol, Generic[T]):
    rowcount: str
    page: int
    pagesize: int
    serviceid: str
    type: str
    vcode: str
    message: str
    messagedetail: str
    datas: List[T]

    def __len__(self) -> int:
        ...

    def __getitem__(self, key: int) -> T:
        ...

    def to_json(self) -> str:
        ...

    @classmethod
    def from_json(cls: Type[T], s: str) -> Optional[T]:
        ...


def result_class(cls: Type[T]) -> Type[Result[T]]:
    @dataclass
    class _Result(Jsonable, Result[T]):
        rowcount: int
        page: int
        pagesize: int
        serviceid: str
        type: str
        vcode: str
        message: str
        messagedetail: str
        datas: List[cls]

        def __len__(self) -> int:
            return len(self.datas or [])

        def __getitem__(self, key: int) -> T:
            return self.datas[key]

    return cast(Type[Result[T]], _Result)


class Session(HttpSocket):
    _result_classes: Dict[Type[T], Type[Result[T]]] = {}

    def __init__(self, host: str, port: int,
                 user_id: str, password: str):
        super().__init__(host, port)
        self._user_id = user_id
        self._password = password
        self._cookies: Dict[str, str] = {}

    def create_request(self) -> HttpRequest:
        request = HttpRequest("/hncjb/reports/crud", method="POST")
        request.add_header("Host", self.url) \
            .add_header("Connection", "keep-alive") \
            .add_header("Accept", "application/json, text/javascript, */*; q=0.01") \
            .add_header("Origin", f"http://{self.url}") \
            .add_header("X-Requested-With", "XMLHttpRequest") \
            .add_header("User-Agent",
                        "Mozilla/5.0 (Windows NT 5.1) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/39.0.2171.95 Safari/537.36") \
            .add_header("Content-Type", "multipart/form-data;charset=UTF-8") \
            .add_header("Referer", f"http://{self.url}/hncjb/pages/html/index.html") \
            .add_header("Accept-Encoding", "gzip, deflate") \
            .add_header("Accept-Language", "zh-CN,zh;q=0.8")
        if self._cookies:
            request.add_header(
                "Cookie", '; '.join((f'{k}={v}' for k, v in self._cookies.items())))
        return request

    def build_request(self, content: str) -> HttpRequest:
        return self.create_request().add_body(content)

    def request(self, content: str):
        req = self.build_request(content).to_bytes()
        # print(f"{req=}")
        self.write_bytes(req)

    def request_service(self, params_or_id: Union[Any, str]):
        req = self.service_to_json(params_or_id)
        self.request(req)

    def service_to_json(self, params_or_id: Union[Any, str]):
        service = None
        if isinstance(params_or_id, str):  # id
            service = Service.new(Params(params_or_id),
                                  self._user_id, self._password)
        else:  # params
            service = Service.new(params_or_id, self._user_id, self._password)
        return service.to_json()

    def get_result(self, cls: Type[T]) -> Optional[Result[T]]:
        result_cls = self._result_classes.setdefault(cls, result_class(cls))
        return self.result_from_json(result_cls, self.read_body())

    def result_from_json(self, cls: Type[U], json: str) -> Optional[U]:
        return cls.from_json(json)

    def login(self) -> str:
        self.request_service('loadCurrentUser')
        header = self.read_header()
        cookies = header.get("set-cookie", [])
        for cookie in cookies:
            m = re.search(r'([^=]+?)=(.+?);', cookie)
            if m:
                self._cookies[m.group(1)] = m.group(2)
        self.read_body(header)
        self.request_service(
            Syslogin(self._user_id, self._password))
        return self.read_body()

    def logout(self) -> str:
        self.request_service('syslogout')
        return self.read_body()

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, e_t, e_v, t_b):
        self.logout()
        self.close()

    @staticmethod
    def use(id='002') -> 'Session':
        return Session(conf.host, conf.port,
                       conf.users[id].id, conf.users[id].pwd)


@dataclass
@params(id='syslogin')
class Syslogin:
    username: str
    passwd: str


@dataclass
@params(id='executeSncbxxConQ')
class CbxxQuery:
    idcard: str = jfield(name='aac002')

    @staticmethod
    def new(idcard=''):
        return CbxxQuery(idcard=idcard)


def match(value, dict: Dict, fail=lambda v: f'未知值: {v}'):
    return dict.get(value, fail(value))


class _Sbstate():
    #cbstate: Optional[str] = None
    #jfstate: Optional[str] = None

    @property
    def cbstate_ch(self: Any):
        return match(self.cbstate,
                     {
                         "0": "未参保",
                         "1": "正常参保",
                         "2": "暂停参保",
                         "4": "终止参保",
                     })

    @property
    def jfstate_ch(self: Any):
        return match(self.jfstate,
                     {
                         "1": "参保缴费",
                         "2": "暂停缴费",
                         "3": "终止缴费",
                     })

    @property
    def jbstate_cn(self: Any):
        return Sbstate.get_jbstate_cn(self.jfstate, self.cbstate)

    @staticmethod
    def get_jbstate_cn(jfstate, cbstate):
        if jfstate == '1':
            if cbstate == '1':
                return '正常缴费人员'
            else:
                return f'未知类型参保缴费人员: {cbstate}'
        elif jfstate == '2':
            if cbstate == '2':
                return '暂停缴费人员'
            else:
                return f'未知类型暂停缴费人员: {cbstate}'
        elif jfstate == '3':
            if cbstate == '1':
                return '正常待遇人员'
            elif cbstate == '2':
                return '暂停待遇人员'
            elif cbstate == '4':
                return '终止参保人员'
            else:
                return f'未知类型终止缴费人员: {cbstate}'
        elif jfstate is None:
            return '未参保'
        else:
            return f'未知类型人员: {jfstate}, {cbstate}'


@dataclass
class Sbstate(_Sbstate):
    cbstate: Optional[str] = jfield('aac008', default=None)  # 参保状态
    jfstate: Optional[str] = jfield('aac031', default=None)  # 缴费状态


@dataclass
class Cbxx(Sbstate):
    pid: Optional[int] = jfield('aac001', default=None)  # 个人编号
    idcard: Optional[str] = jfield('aac002', default=None)  # 身份证号码
    name: str = jfield('aac003', default='')
    birthday: Optional[int] = jfield('aac006', default=None)

    cbdate: Optional[str] = jfield('aac049', default='')  # 参保时间
    sfcode: str = jfield('aac066', default='')  # 参保身份编码
    agancy: str = jfield('aaa129', default='')  # 社保机构
    optime: str = jfield('aae036', default='')  # 经办时间
    qhcode: Optional[str] = jfield('aaf101', default='')  # 行政区划编码
    czname: str = jfield('aaf102', default='')  # 村组名称
    csname: Optional[str] = jfield('aaf103', default='')  # 村社区名称

    @property
    def jbclass(self):
        return match(self.sfcode,
                     {
                         "011": "普通参保人员",
                         "021": "残一级",
                         "022": "残二级",
                         "031": "特困一级",
                         "051": "贫困人口一级",
                         "061": "低保对象一级",
                         "062": "低保对象二级",
                     },
                     lambda v: f'未知身份类型: {v}')

    @property
    def valid(self):
        return self.idcard is not None


@dataclass
@params(id='cbshQuery')
class CbshQuery(Page):
    aaf013: str = ""
    aaf030: str = ""
    aae011: str = ""
    aae036: str = ""
    aae036s: str = ""
    aae014: str = ""
    aac009: str = ""
    aac002: str = ""
    aac003: str = ""
    sfccb: str = ""

    start_date: str = jfield('aae015', default='')
    end_date: str = jfield('aae015s', default='')
    shzt: str = jfield('aae016', default='1')

    @staticmethod
    def new(start_date: str = '', end_date: str = '', shzt: str = '1'):
        return CbshQuery(start_date=start_date,
                         end_date=end_date,
                         shzt=shzt,
                         pagesize=500)


@dataclass
class Cbsh:
    idcard: str = jfield('aac002')
    name: str = jfield('aac003')
    birthday: int = jfield('aac006')
