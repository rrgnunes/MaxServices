from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Volume_vendido(Base):
    __tablename__ = 'volume_vendido'
    codigo = Column(INTEGER, primary_key=True)
    id_lmc = Column(INTEGER)
    id_tanque = Column(INTEGER)
    id_bico = Column(INTEGER)
    preco = Column(DECIMAL)
    fechamento = Column(DECIMAL)
    abertura = Column(DECIMAL)
    afericao = Column(DECIMAL)
    vendas_bico = Column(DECIMAL)
