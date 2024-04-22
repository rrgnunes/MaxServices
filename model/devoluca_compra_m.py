from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Devoluca_compra_m(Base):
    __tablename__ = 'devoluca_compra_m'
    codigo = Column(INTEGER, primary_key=True)
    data = Column(DATE)
    fk_fornecedor = Column(INTEGER)
    total = Column(DECIMAL)
    numero_compra = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    situacao = Column(VARCHAR)
    fk_usuario = Column(INTEGER)
    observacao = Column(VARCHAR)
