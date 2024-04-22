from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tabela_icms(Base):
    __tablename__ = 'tabela_icms'
    origem = Column(VARCHAR, primary_key=True)
    ac = Column(DECIMAL)
    al = Column(DECIMAL)
    am = Column(DECIMAL)
    ap = Column(DECIMAL)
    ba = Column(DECIMAL)
    ce = Column(DECIMAL)
    df = Column(DECIMAL)
    es = Column(DECIMAL)
    go = Column(DECIMAL)
    ma = Column(DECIMAL)
    mg = Column(DECIMAL)
    ms = Column(DECIMAL)
    mt = Column(DECIMAL)
    pa = Column(DECIMAL)
    pb = Column(DECIMAL)
    pe = Column(DECIMAL)
    p_i = Column(DECIMAL)
    pr = Column(DECIMAL)
    rj = Column(DECIMAL)
    ro = Column(DECIMAL)
    rn = Column(DECIMAL)
    rr = Column(DECIMAL)
    rs = Column(DECIMAL)
    sc = Column(DECIMAL)
    se = Column(DECIMAL)
    sp = Column(DECIMAL)
    t_o = Column(DECIMAL)
