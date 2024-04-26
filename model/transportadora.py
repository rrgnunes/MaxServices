from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Transportadora(db.Model):
    __tablename__ = 'transportadora'
    codigo = Column(INTEGER, primary_key=True)
    pessoa = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    ie = Column(VARCHAR)
    nome = Column(VARCHAR)
    apelido = Column(VARCHAR)
    endereco = Column(VARCHAR)
    numero = Column(VARCHAR)
    bairro = Column(VARCHAR)
    cod_cidade = Column(INTEGER)
    cidade = Column(VARCHAR)
    uf = Column(VARCHAR)
    cep = Column(VARCHAR)
    placa = Column(VARCHAR)
    ufplaca = Column(VARCHAR)
    rntc = Column(VARCHAR)
    ativo = Column(VARCHAR)
    empresa = Column(INTEGER)
    renavam = Column(VARCHAR)
    motorista = Column(VARCHAR)
    cpf_motorista = Column(VARCHAR)
