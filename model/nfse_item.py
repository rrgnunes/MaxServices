from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Nfse_item(db.Model):
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
