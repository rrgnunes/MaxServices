from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necess�rio
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mdfe_encerrar(Base):
    __tablename__ = 'mdfe_encerrar'
    chave = Column(VARCHAR, primary_key=True)
    protocolo = Column(VARCHAR)
    fk_empresa = Column(INTEGER)
    situacao = Column(VARCHAR)
