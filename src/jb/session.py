from typing import Optional, TypeVar, Generic, List, ClassVar, Union, Type, Dict, Final
from ..httpsocket import HttpSocket, HttpRequest
from dataclasses import dataclass, field, MISSING, fields
from dataclasses_json import config, DataClassJsonMixin
import re


def json(*, name: Optional[str] = None, default=MISSING, factory=MISSING):
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


def params(cls=None, /, *, id='',
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


U = TypeVar('U', bound=Jsonable)


@dataclass
class Result(Jsonable, Generic[U]):
    rowcount: str
    page: int
    pagesize: int
    serviceid: str
    type: str
    vcode: str
    message: str
    messagedetail: str
    datas: List[U]

    def __len__(self):
        return len(self.datas or [])

    def __getitem__(self, key: int) -> U:
        return self.datas[key]


class Session(HttpSocket):
    _user_id: str
    _password: str
    _session_id: Optional[str] = None
    _cxcookie: Optional[str] = None

    def __init__(self, host: str, port: int,
                 user_id: str, password: str):
        self._user_id = user_id
        self._password = password

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
        if self._session_id:
            request.add_header("Cookie",
                               f"jsessionid_ylzcbp={self._session_id}; "
                               f"cxcookie={self._cxcookie}")
        return request

    def build_request(self, content: str) -> HttpRequest:
        return self.create_request().add_body(content)

    def request(self, content: str):
        self.write_bytes(self.build_request(content).to_bytes())

    def request_service(self, params_or_id: Union[Parameters, str]):
        self.request(self.service_to_json(params_or_id))

    def service_to_json(self, params_or_id: Union[Parameters, str]):
        service = None
        if isinstance(params_or_id, str):  # id
            service = Service(Parameters(params_or_id),
                              self._user_id, self._password)
        else:  # params
            service = Service(params_or_id, self._user_id, self._password)
        return service.to_json()

    def get_result(self, cls: Type[U]) -> Result[U]:
        return self.result_from_json(cls, self.read_body())

    def result_from_json(self, cls: Type[U], json: str) -> Result[U]:
        return Result[U].from_json(json)

    def login(self) -> str:
        self.request_service('loadCurrentUser')
        header = self.read_header()
        cookies = header.get("set-cookie", [])
        if cookies:
            for cookie in cookies:
                m = re.search(r'jsessionid_ylzcbp=(.+?);', cookie)
                if m:
                    self._session_id = m.group(1)
                    continue
                m = re.search(r'cxcookie=(.+?);', cookie)
                if m:
                    self._cxcookie = m.group(1)
        self.read_body(header)
        self.request_service(
            Syslogin(self._user_id, self._password))  # type: ignore
        return self.read_body()

    def logout(self) -> str:
        self.request_service('syslogout')
        return self.read_body()


@params(id='syslogin')
class Syslogin(Parameters):
    username: str
    passwd: str
