# coding: utf-8
__author__ = 'Jerry'
"公众号：Python编程与实战,欢迎关注"

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql

from 胡润排行榜.enum_type import EnumType

pymysql.install_as_MySQLdb()

engine = create_engine('mysql://', echo=True)  # TODO  填写自己的mysql数据库账号密码
db_session = sessionmaker(bind=engine)
Base = declarative_base()


class Process(Base):
    __tablename__ = "hurun_rank"

    id = Column(Integer, primary_key=True)
    name_id = Column(Integer())
    name = Column(String(100))
    ranking = Column(Integer())
    birthday = Column(String(10))
    name_cn = Column(String(20))
    industry = Column(String(100))
    year = Column(String(10))
    wealth = Column(String(20))

    # 把SQLAlchemy查询对象转换成字典
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def init_db():  # 初始化表
    Base.metadata.create_all(engine)


def save_db(s):
    """
    save to Mysql
    :return:
    """
    session = db_session()
    new = Process(name=s.get(EnumType.NAME), name_id=s.get(EnumType.NAME_ID),
                  ranking=s.get(EnumType.RANKING), year=s.get(EnumType.YEAR),
                  birthday=s.get(EnumType.BIRTHDAY), name_cn=s.get(EnumType.NAME_CN),
                  industry=s.get(EnumType.INDUSTRY), wealth=s.get(EnumType.WEALTH))

    session.add(new)
    session.commit()
    session.close()


def que(name, year):
    session = db_session()
    company_list = session.query(Process).filter(Process.name == name, Process.year == year).first()
    session.close()
    return company_list


def search(name, year):
    session = db_session()
    company_list = session.query(Process).filter(Process.name == name, Process.year == year).all()
    session.close()
    return company_list


if __name__ == '__main__':
    pass
