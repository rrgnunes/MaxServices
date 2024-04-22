from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Inventario(Base):
    __tablename__ = 'inventario'
    fk_produto = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    codigo = Column(INTEGER)
    tributacao = Column(VARCHAR)
    pr_custo = Column(DECIMAL)
    qtd = Column(DECIMAL)
    total = Column(DECIMAL)
