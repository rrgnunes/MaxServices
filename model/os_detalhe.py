from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Os_detalhe(db.Model):
    __tablename__ = 'os_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    fk_os_master = Column(INTEGER)
    fk_funcionario = Column(INTEGER)
    fk_produto = Column(INTEGER)
    data_inicio = Column(DATE)
    hora_inicio = Column(TIME)
    data_termino = Column(DATE)
    hora_termino = Column(TIME)
    discriminacao = Column(VARCHAR)
    qtd = Column(DECIMAL)
    preco = Column(DECIMAL)
    total = Column(DECIMAL)
    fk_usuario = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    tipo = Column(VARCHAR)
    situacao = Column(VARCHAR)
    tamanho = Column(VARCHAR)
    detalhe = Column(VARCHAR)
    nome = Column(VARCHAR)
    numero = Column(VARCHAR)
    cor = Column(VARCHAR)
