from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necess�rio
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Nfse_item(Base):
    __tablename__ = 'nfse_item'
    id_nfse_item = Column(INTEGER, primary_key=True)
    id_nfse = Column(INTEGER)
    id_item = Column(INTEGER)
    id_produto = Column(BIGINT)
    qt = Column(NUMERIC)
    vl_unit = Column(NUMERIC)
    vl_total = Column(BIGINT)
    perc_issqn = Column(DECIMAL)
    vl_issqn = Column(DECIMAL)
