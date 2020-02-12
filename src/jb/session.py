from typing import Optional, TypeVar, Generic, List, ClassVar, Union, Type, Dict, Final, Protocol
from ..httpsocket import HttpSocket, HttpRequest
from dataclasses import dataclass, field, MISSING, fields
from dataclasses_json import config, DataClassJsonMixin
import re
from .jb_internal import session_conf as conf


def json(name: Optional[str] = None, default=MISSING, *, factory=MISSING):
    if default != MISSING:
        return field(metadata=config(field_name=name), default=default)
    else:
        return field(metadata=config(field_name=name), default_factory=factory)


class Jsonable(DataClassJsonMixin):
    def to_json(self):
        return super().to_json(separators=(',', ':'))


@dataclass
class Parameters(Jsonable):
    @property
    def service_id(self):
        return self._service_id

    def __init__(self, id: str):
        self._service_id = id


@dataclass
class Page:
    page: int = 1
    pagesize: int = 15
    filtering: List[Dict[str, str]] = json(factory=list)
    sorting: List[Dict[str, str]] = json(factory=list)
    totals: List[Dict[str, str]] = json(factory=list)


def params(cls=None, / , *, id='',
           page: Optional[Page] = None, **kwargs):

    def wrap(cls):
        cls = dataclass(cls, **kwargs)
        cls._service_id = id
        if page:
            page_ = page
            @dataclass
            class DataPage(cls):
                page: int = page_.page
                pagesize: int = page_.pagesize
                filtering: List[Dict[str, str]] = json(
                    factory=lambda: list(page_.filtering))
                sorting: List[Dict[str, str]] = json(
                    factory=lambda: list(page_.sorting))
                totals: List[Dict[str, str]] = json(
                    factory=lambda: list(page_.totals))
            return DataPage
        return cls

    if cls == None:  # called by params(id=?)
        return wrap
    return wrap(cls)


@dataclass
class Service(Jsonable):
    serviceid: str = ''
    target: str = ''
    sessionid: Optional[str] = None
    loginname: str = ''
    password: str = ''
    params: Optional[Parameters] = None
    datas: Optional[List[Parameters]] = None

    def __init__(self, params: Parameters, user_id: str, password: str):
        self.serviceid = params.service_id
        # print(self.serviceid)
        self.loginname = user_id
        self.password = password
        self.params = params
        self.datas = [params]


T = TypeVar('T')
U = TypeVar('U', bound=Jsonable)


class Result(Protocol, Generic[U]):
    rowcount: str
    page: int
    pagesize: int
    serviceid: str
    type: str
    vcode: str
    message: str
    messagedetail: str
    datas: List[U]

    def __len__(self) -> int:
        ...

    def __getitem__(self, key: int) -> U:
        ...

    def to_json(self) -> str:
        ...

    @classmethod
    def from_json(cls: Type[T],
                  s: str,
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  infer_missing=False,
                  **kw) -> T:
        ...


def result(cls: Type[U]) -> Type[Result[U]]:
    cls = dataclass(cls)
    @dataclass
    class _Result(Jsonable):
        rowcount: str
        page: int
        pagesize: int
        serviceid: str
        type: str
        vcode: str
        message: str
        messagedetail: str
        datas: List[cls]  # type: ignore

        def __len__(self):
            return len(self.datas or [])

        def __getitem__(self, key: int) -> U:
            return self.datas[key]

    return _Result


class Session(HttpSocket):
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

    def request_service(self, params_or_id: Union[Parameters, str]):
        req = self.service_to_json(params_or_id)
        self.request(req)

    def service_to_json(self, params_or_id: Union[Parameters, str]):
        service = None
        if isinstance(params_or_id, str):  # id
            service = Service(Parameters(params_or_id),
                              self._user_id, self._password)
        else:  # params
            service = Service(params_or_id, self._user_id, self._password)
        return service.to_json()

    def get_result(self, cls: Type[U]) -> U:
        return self.result_from_json(cls, self.read_body())

    def result_from_json(self, cls: Type[U], json: str) -> U:
        return cls.from_json(json)

    def login(self) -> str:
        self.request_service('loadCurrentUser')
        header = self.read_header()
        cookies = header.get("set-cookie", [])
        for cookie in cookies:  # type: ignore
            m = re.search(r'([^=]+?)=(.+?);', cookie)
            if m:
                self._cookies[m.group(1)] = m.group(2)
        self.read_body(header)
        self.request_service(
            Syslogin(self._user_id, self._password))  # type: ignore
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


@params(id='syslogin')
class Syslogin(Parameters):
    username: str
    passwd: str


@params(id='executeSncbxxConQ')
class CbxxQuery(Parameters):
    idcard: str = json(name='aac002')


@dataclass
class Sbstate:
    cbstate: Optional[str] = json('aac008', None)  # 参保状态
    jfstate: Optional[str] = json('aac031', None)  # 缴费状态

    @property
    def cbstate_ch(self):
        return {
            "0": "未参保",
            "1": "正常参保",
            "2": "暂停参保",
            "4": "终止参保",
        }.get(self.cbstate,
              f'未知值: {self.cbstate}')

    @property
    def jfstate_ch(self):
        return {
            "1": "参保缴费",
            "2": "暂停缴费",
            "3": "终止缴费",
        }.get(self.jfstate,
              f'未知值: {self.jfstate}')

    @property
    def jbstate_cn(self):
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
        elif jfstate == None:
            return '未参保'
        else:
            return f'未知类型人员: {jfstate}, {cbstate}'


@result
class Cbxx(Jsonable, Sbstate):
    pid: Optional[int] = json('aac001', None)  # 个人编号
    idcard: Optional[str] = json('aac002', None)  # 身份证号码
    name: str = json('aac003', '')
    birthday: Optional[int] = json('aac006', None)

    cbdate: str = json('aac049', '')  # 参保时间
    sfcode: str = json('aac066', '')  # 参保身份编码
    agancy: str = json('aaa129', '')  # 社保机构
    optime: str = json('aae036', '')  # 经办时间
    qhcode: str = json('aaf101', '')  # 行政区划编码
    czname: str = json('aaf102', '')  # 村组名称
    csname: str = json('aaf103', '')  # 村社区名称

    @property
    def jbclass(self):
        return {
            "011": "普通参保人员",
            "021": "残一级",
            "022": "残二级",
            "031": "特困一级",
            "051": "贫困人口一级",
            "061": "低保对象一级",
            "062": "低保对象二级",
        }.get(self.sfcode,
              f'未知身份类型: {self.sfcode}')

    @property
    def valid(self):
        return self.idcard is not None
