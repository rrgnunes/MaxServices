from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cte_detalhe(Base):
    __tablename__ = 'cte_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    fk_cte_master = Column(INTEGER)
    numero = Column(INTEGER)
    chave = Column(VARCHAR)
    preco = Column(DECIMAL)
    qtd = Column(DECIMAL)
    total = Column(DECIMAL)
    unidade = Column(VARCHAR)
    fk_destinatario = Column(INTEGER)
    descricao = Column(VARCHAR)
