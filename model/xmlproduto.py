from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Xmlproduto(Base):
    __tablename__ = 'xmlproduto'
    id_fornecedor = Column(DOUBLE , primary_key=True)
    id_produto_forn = Column(VARCHAR, primary_key=True)
    id_produto_local = Column(DOUBLE , primary_key=True)
    qtd_e = Column(DECIMAL)
    qtd_s = Column(DECIMAL)
    un_e = Column(VARCHAR)
    un_s = Column(VARCHAR)
    fk_grupo = Column(INTEGER)
    fkempresa = Column(INTEGER)
