from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Comanda_itens(Base):
    __tablename__ = 'comanda_itens'
    codigo = Column(INTEGER, primary_key=True)
    fk_comanda_pessoa = Column(INTEGER)
    fk_produto = Column(INTEGER)
    qtd = Column(DECIMAL)
    preco = Column(DECIMAL)
    total = Column(DECIMAL)
    percentual = Column(DECIMAL)
    situacao = Column(VARCHAR)
    data_hora = Column(TIMESTAMP)
    observacao = Column(BLOB)
