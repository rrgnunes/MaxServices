from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tradutor(Base):
    __tablename__ = 'tradutor'
    codigo = Column(INTEGER, primary_key=True)
    codigo_idioma = Column(INTEGER)
    tela = Column(VARCHAR)
    objeto = Column(VARCHAR)
    texto_pt_br = Column(VARCHAR)
    texto_traduzido = Column(VARCHAR)
