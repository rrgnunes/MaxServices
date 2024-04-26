from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class G_ctrl(db.Model):
    __tablename__ = 'g_ctrl'
    ctrl_id = Column(INTEGER, primary_key=True)
    ctrl_codigo = Column(VARCHAR)
    ctrl_descricao = Column(VARCHAR)
    ctrl_valor = Column(VARCHAR)
    ctrl_sistema = Column(VARCHAR)
    ctrl_modulo = Column(VARCHAR)
    ctrl_atualiza = Column(CHAR)
