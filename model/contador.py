from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Contador(db.Model):
    __tablename__ = 'contador'
    codigo = Column(SMALLINT, primary_key=True)
    nome = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    cpf = Column(VARCHAR)
    crc = Column(VARCHAR)
    endereco = Column(VARCHAR)
    numero = Column(VARCHAR)
    complemento = Column(VARCHAR)
    cep = Column(VARCHAR)
    bairro = Column(VARCHAR)
    cod_mun = Column(INTEGER)
    fone = Column(VARCHAR)
    fax = Column(VARCHAR)
    email = Column(VARCHAR)
    uf = Column(VARCHAR)
    fk_usuario = Column(INTEGER)
    fk_empresa = Column(INTEGER)
