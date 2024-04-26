from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Servicos(db.Model):
    __tablename__ = 'servicos'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    unidade = Column(VARCHAR)
    pr_custo = Column(DECIMAL)
    margem_lucro = Column(DECIMAL)
    pr_venda = Column(DECIMAL)
    comiss_vista = Column(DECIMAL)
    comss_prazo = Column(DECIMAL)
    ativo = Column(VARCHAR)
    paga_comiss = Column(VARCHAR)
    observacao = Column(VARCHAR)
