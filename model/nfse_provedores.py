from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Nfse_provedores(Base):
    __tablename__ = 'nfse_provedores'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    fk_cidade = Column(INTEGER)
