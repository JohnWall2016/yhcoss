from typing import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as _DBSession
from sqlalchemy.orm.query import Query as _DBQuery

from .jb_internal import mysql_engine_jzfp2020

engine = create_engine(mysql_engine_jzfp2020)

Base: Any = declarative_base()


class FPData():
    no = Column(Integer, primary_key=True)  # 序号
    xzj = Column(String)  # 乡镇街
    csq = Column(String)  # 村社区
    address = Column(String)  # 地址
    name = Column(String)  # 姓名
    idcard = Column(String)  # 身份证号码
    birthday = Column(String)  # 出生日期
    pkrk = Column(String)  # 贫困人口
    pkrk_date = Column('pkrkdate', String)  # 贫困人口日期
    tkry = Column(String)  # 特困人员
    tkry_date = Column('tkrydate', String)  # 特困人员日期
    qedb = Column(String)  # 全额低保人员
    qedb_date = Column('qedbdate', String)  # 全额低保人员日期
    cedb = Column(String)  # 差额低保人员
    cedb_date = Column('cedbdate', String)  # 差额低保人员日期
    yejc = Column(String)  # 一二级残疾人员
    yejc_date = Column('yejcdate', String)  # 一二级残疾人员日期
    ssjc = Column(String)  # 三四级残疾人员
    ssjc_date = Column('ssjcdate', String)  # 三四级残疾人员日期
    sypkry = Column(String)  # 属于贫困人员
    jbrdsf = Column(String)  # 居保认定身份
    jbrdsf_firstdate = Column('jbrdsffirstdate', String)  # 居保认定身份最初日期
    jbrdsf_lastdate = Column('jbrdsflastdate', String)  # 居保认定身份最后日期
    jbcbqk = Column(String)  # 居保参保情况
    jbcbqk_date = Column('jbcbqkdate', String)  # 居保参保情况日期


class FPHistoryData(Base, FPData):
    __tablename__ = 'fphistorydata'


T = TypeVar('T')

class Query(Generic[T], _DBQuery):
    def filter(self, *criterion) -> 'Query[T]': ...
    def filter_by(self, **kwargs) -> 'Query[T]': ...
    def first(self) -> Optional[T]: ...

class DBSession(_DBSession):
    def query(self, *entities, **kwargs) -> Query: ...
    def query(self, entity1: Type[T], **kwargs) -> Query[T]: ...

_Session = sessionmaker(bind=engine)


class Session:
    def __init__(self):
        self._session = _Session()

    def __enter__(self) -> DBSession:
        return self._session

    def __exit__(self, e_t, e_v, t_b):
        self._session.close()
