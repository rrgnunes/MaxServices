from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sped_participantes(Base):
    __tablename__ = 'sped_participantes'
    codigo = Column(INTEGER, primary_key=True)
    cod_part = Column(INTEGER)
    nome = Column(VARCHAR)
    cod_pais = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    cpf = Column(VARCHAR)
    ie = Column(VARCHAR)
    cod_mun = Column(INTEGER)
    endereco = Column(VARCHAR)
    numero = Column(VARCHAR)
    complemento = Column(VARCHAR)
    bairro = Column(VARCHAR)
    fk_sped = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
