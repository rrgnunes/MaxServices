from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cte_destinatario(db.Model):
    __tablename__ = 'cte_destinatario'
    codigo = Column(INTEGER, primary_key=True)
    nome = Column(VARCHAR)
    endereco = Column(VARCHAR)
    numero = Column(VARCHAR)
    bairro = Column(VARCHAR)
    id_cidade = Column(INTEGER)
    cidade = Column(VARCHAR)
    cep = Column(VARCHAR)
    uf = Column(VARCHAR)
    pessoa = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    ie = Column(VARCHAR)
    fone = Column(VARCHAR)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
    ativo = Column(INTEGER)
