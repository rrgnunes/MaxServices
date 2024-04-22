from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sped(Base):
    __tablename__ = 'sped'
    codigo = Column(INTEGER, primary_key=True)
    data_ini = Column(DATE)
    data_fim = Column(DATE)
    dtemissao = Column(DATE)
    remessa = Column(VARCHAR)
    semmovimento = Column(VARCHAR)
    recibo = Column(VARCHAR)
    fk_contador = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
