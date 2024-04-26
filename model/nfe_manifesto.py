from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Nfe_manifesto(db.Model):
    __tablename__ = 'nfe_manifesto'
    codigo = Column(INTEGER, primary_key=True)
    numero = Column(VARCHAR)
    chave = Column(VARCHAR)
    serie = Column(VARCHAR)
    nome = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    ie = Column(VARCHAR)
    nsu = Column(VARCHAR)
    valor = Column(DECIMAL)
    dt_entrada = Column(DATE)
    dt_emissao = Column(DATE)
    situacao = Column(VARCHAR)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
    caminho_xml = Column(VARCHAR)
    xml = Column(BLOB)
    gerou = Column(VARCHAR)
