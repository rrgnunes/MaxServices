from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Comanda_receb_parcial(Base):
    __tablename__ = 'comanda_receb_parcial'
    codigo = Column(INTEGER, primary_key=True)
    fk_comandamaster = Column(INTEGER)
    observacao = Column(VARCHAR)
    fk_formapag = Column(INTEGER)
    descricao_formapag = Column(VARCHAR)
    datacad = Column(TIMESTAMP)
    valor_pago = Column(NUMERIC)
