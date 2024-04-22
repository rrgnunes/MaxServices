from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vendas_fpg(Base):
    __tablename__ = 'vendas_fpg'
    codigo = Column(INTEGER, primary_key=True)
    vendas_master = Column(INTEGER)
    id_forma = Column(INTEGER)
    valor = Column(DECIMAL)
    fk_usuario = Column(INTEGER)
    situacao = Column(VARCHAR)
    tipo = Column(VARCHAR)
    fez_tef = Column(SMALLINT)
    codigotransacao = Column(VARCHAR)
    datapagamento = Column(TIMESTAMP)
    rede = Column(VARCHAR)
    nsu = Column(VARCHAR)
    codigofinalizacao = Column(VARCHAR)
    cancelamento = Column(VARCHAR)
