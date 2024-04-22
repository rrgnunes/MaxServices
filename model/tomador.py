from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tomador(Base):
    __tablename__ = 'tomador'
    codigo = Column(INTEGER, primary_key=True)
    razao = Column(VARCHAR)
    fantasia = Column(VARCHAR)
    fone = Column(VARCHAR)
    endereco = Column(VARCHAR)
    numero = Column(VARCHAR)
    bairro = Column(VARCHAR)
    codmun = Column(INTEGER)
    municipio = Column(VARCHAR)
    uf = Column(VARCHAR)
    cep = Column(VARCHAR)
    fkempresa = Column(INTEGER)
    tipo = Column(VARCHAR)
    ie = Column(VARCHAR)
    cnpj = Column(VARCHAR)
