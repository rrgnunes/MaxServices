from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Volume_recebido(db.Model):
    __tablename__ = 'volume_recebido'
    codigo = Column(INTEGER, primary_key=True)
    id_lmc = Column(INTEGER)
    n_fiscal = Column(INTEGER)
    obs_fiscal = Column(VARCHAR)
    id_tanque = Column(INTEGER)
    vol_recebido = Column(DECIMAL)
