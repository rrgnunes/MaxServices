from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Fechamento_lmc(Base):
    __tablename__ = 'fechamento_lmc'
    codigo = Column(INTEGER, primary_key=True)
    id_lmc = Column(INTEGER)
    vendas_bico = Column(DECIMAL)
    estoq_estrutural = Column(DECIMAL)
    estoq_fechamento = Column(DECIMAL)
    valor_vendas = Column(DECIMAL)
    valor_acumulado = Column(DECIMAL)
    perdas_sobras = Column(DECIMAL)
