from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cbr_config(Base):
    __tablename__ = 'cbr_config'
    id_empresa = Column(INTEGER, primary_key=True)
    dirrecebe = Column(VARCHAR)
    direnvia = Column(VARCHAR)
    dirrecebebkp = Column(VARCHAR)
    vlrtarifaboleta = Column(NUMERIC)
    tipocobranca = Column(VARCHAR)
    codbanco = Column(SMALLINT)
    agencia = Column(SMALLINT)
    agenciadig = Column(CHAR)
    conta = Column(VARCHAR)
    contadig = Column(CHAR)
    codcedente = Column(VARCHAR)
    codcedentedig = Column(CHAR)
    convenio = Column(VARCHAR)
    carteira = Column(VARCHAR)
    modalidade = Column(VARCHAR)
    especiedoc = Column(CHAR)
    cobmoeda = Column(VARCHAR)
    cobaceite = Column(VARCHAR)
    localpagto = Column(VARCHAR)
    instrucao1 = Column(VARCHAR)
    instrucao2 = Column(VARCHAR)
    layout = Column(VARCHAR)
    valormorajuros = Column(NUMERIC)
    percentualmulta = Column(NUMERIC)
    layoutboleto = Column(VARCHAR)
