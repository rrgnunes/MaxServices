from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Etiquetas(Base):
    __tablename__ = 'etiquetas'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    largura = Column(DECIMAL)
    altura = Column(DECIMAL)
    esquerda = Column(DECIMAL)
    topo = Column(DECIMAL)
    colunas = Column(INTEGER)
    espacamento = Column(DECIMAL)
    barra_altura = Column(DECIMAL)
    barra_largura = Column(DECIMAL)
    barra_fina = Column(DECIMAL)
    porta = Column(VARCHAR)
    modelo = Column(VARCHAR)
    dpi = Column(VARCHAR)
    backfeed = Column(VARCHAR)
