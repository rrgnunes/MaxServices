import time
import random
from datetime import datetime
import sys
import os
from campanha_mensagens import gerar_cumprimento

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from funcoes.funcoes_zap import *
from funcoes.funcoes import carregar_configuracoes, inicializa_conexao_mysql, print_log


# ---------------- HORÁRIOS FIXOS ----------------
def gerar_horarios():
    inicio = 8 * 60   # 08:00
    fim    = 18 * 60  # 18:00
    return inicio, fim

def minutos_para_horas(minutos):
    horas = minutos // 60
    minutos_restantes = minutos % 60
    return f"{horas:02d}:{minutos_restantes:02d}"

def atualizar_horarios():
    global inicio_minutos, fim_minutos, horario_inicio, horario_fim
    inicio_minutos, fim_minutos = gerar_horarios()
    horario_inicio = minutos_para_horas(inicio_minutos)
    horario_fim    = minutos_para_horas(fim_minutos)
    print_log(f"Hoje as mensagens serão enviadas entre {horario_inicio} e {horario_fim}.")

atualizar_horarios()


# ---------------- INICIALIZAÇÃO ----------------
name_session = "00000000000000"
token = generate_token(name_session)
parametros.TOKEN_ZAP = token['token']
retorno = start_session(name_session)

parametros.BASEMYSQL = 'maxservices'
carregar_configuracoes()
inicializa_conexao_mysql()

nome_servico = 'Campanha ZAP'
print_log("Iniciando serviço", nome_servico)


# ---------------- BUSCA INICIAL ----------------
def buscar_contatos():
    if parametros.MYSQL_CONNECTION is None or not parametros.MYSQL_CONNECTION.is_connected():
        inicializa_conexao_mysql()

    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(f'''
        SELECT codigo, REPLACE(SUBSTRING_INDEX(cl.telefone, ' ', 2), ' ', '') as telefone
        FROM cliente_lead cl
        WHERE (
            cl.cnae LIKE '%4782201%' OR cl.cnae LIKE '%4711301%' OR cl.cnae LIKE '%4711302%' OR
            cl.cnae LIKE '%4712100%' OR cl.cnae LIKE '%4771704%' OR cl.cnae LIKE '%4732600%' OR
            cl.cnae LIKE '%4741500%' OR cl.cnae LIKE '%4742300%' OR cl.cnae LIKE '%4743100%' OR
            cl.cnae LIKE '%4744001%' OR cl.cnae LIKE '%4744002%' OR cl.cnae LIKE '%4744003%' OR
            cl.cnae LIKE '%4744004%' OR cl.cnae LIKE '%4744005%' OR cl.cnae LIKE '%4744006%' OR
            cl.cnae LIKE '%4744099%' OR cl.cnae LIKE '%4772500%' OR cl.cnae LIKE '%4774100%' OR
            cl.cnae LIKE '%4781400%' OR cl.cnae LIKE '%4782201%' OR cl.cnae LIKE '%4782202%' OR
            cl.cnae LIKE '%4783101%' OR cl.cnae LIKE '%4783102%' OR cl.cnae LIKE '%4755502%' OR
            cl.cnae LIKE '%5611201%' OR cl.cnae LIKE '%5611203%' OR cl.cnae LIKE '%5611204%' OR
            cl.cnae LIKE '%5611205%' OR cl.cnae LIKE '%1053800%' OR cl.cnae LIKE '%1091102%' OR
            cl.cnae LIKE '%4713002%' OR cl.cnae LIKE '%4713004%' OR cl.cnae LIKE '%4713005%' OR
            cl.cnae LIKE '%4721102%' OR cl.cnae LIKE '%4721103%' OR cl.cnae LIKE '%4721104%' OR
            cl.cnae LIKE '%4722901%' OR cl.cnae LIKE '%4722902%' OR cl.cnae LIKE '%4723700%' OR
            cl.cnae LIKE '%4724500%' OR cl.cnae LIKE '%4729601%' OR cl.cnae LIKE '%4729602%' OR
            cl.cnae LIKE '%4729699%' OR cl.cnae LIKE '%4751201%' OR cl.cnae LIKE '%4751202%' OR
            cl.cnae LIKE '%4752100%' OR cl.cnae LIKE '%4753900%' OR cl.cnae LIKE '%4754701%' OR
            cl.cnae LIKE '%4754702%' OR cl.cnae LIKE '%4754703%' OR cl.cnae LIKE '%4755501%' OR
            cl.cnae LIKE '%4755502%' OR cl.cnae LIKE '%4755503%' OR cl.cnae LIKE '%4756300%' OR
            cl.cnae LIKE '%4757100%' OR cl.cnae LIKE '%4759801%' OR cl.cnae LIKE '%4759899%' OR
            cl.cnae LIKE '%4761001%' OR cl.cnae LIKE '%4761002%' OR cl.cnae LIKE '%4761003%' OR
            cl.cnae LIKE '%4762800%' OR cl.cnae LIKE '%4763601%' OR cl.cnae LIKE '%4763602%' OR
            cl.cnae LIKE '%4763603%' OR cl.cnae LIKE '%4763604%' OR cl.cnae LIKE '%4763605%' OR
            cl.cnae LIKE '%4773300%' OR cl.cnae LIKE '%4784900%' OR cl.cnae LIKE '%4785701%' OR
            cl.cnae LIKE '%4785799%' OR cl.cnae LIKE '%4789001%' OR cl.cnae LIKE '%4789002%' OR
            cl.cnae LIKE '%4789003%' OR cl.cnae LIKE '%4789004%' OR cl.cnae LIKE '%4789005%' OR
            cl.cnae LIKE '%4789006%' OR cl.cnae LIKE '%4789007%' OR cl.cnae LIKE '%4789008%' OR
            cl.cnae LIKE '%4789009%' OR cl.cnae LIKE '%4789099%' OR cl.cnae LIKE '%5612100%'
        )
        AND cl.localidade = 'CE'
        AND cl.campanha_enviado IS NULL
    ''')
    obj = cur_con.fetchall()
    cur_con.close()
    return obj


# ---------------- ENVIO ----------------
def iniciar_envio():
    obj_empresas = buscar_contatos()

    if not obj_empresas:
        print_log("Nenhum contato encontrado para enviar.", nome_servico)
        return

    print_log(f"Total de números únicos: {len(obj_empresas)}", nome_servico)
    contador = 0

    for numero in obj_empresas:
        try:
            while True:
                dia_semana    = datetime.now().weekday()
                hora_atual    = datetime.now()
                minutos_atual = hora_atual.hour * 60 + hora_atual.minute

                if dia_semana != datetime.now().weekday():
                    atualizar_horarios()

                if dia_semana in [0,1,2,3,4] and inicio_minutos <= minutos_atual <= fim_minutos:
                    break
                else:
                    print_log("Fora do horário de envio ou fim de semana. Aguardando...", nome_servico)
                    time.sleep(60)

            if parametros.MYSQL_CONNECTION is None or not parametros.MYSQL_CONNECTION.is_connected():
                inicializa_conexao_mysql()

            mensagem_aleatoria = gerar_cumprimento()
            print_log(f'Enviando para o número {numero["telefone"]}', nome_servico)
            retorno = envia_mensagem_zap(name_session, str(numero['telefone']), mensagem_aleatoria)
            print_log(f'O envio para o número {numero["telefone"]} foi um {retorno["status"]}', nome_servico)

            contador += 1
            print_log(f'Enviei {contador} mensagens', nome_servico)

            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute(f'''
                UPDATE cliente_lead 
                SET campanha_enviado = 1 
                WHERE codigo = {numero['codigo']}
            ''')
            cur_con.close()
            parametros.MYSQL_CONNECTION.commit()

            # Ritmo para 550 mensagens/dia
            tempo_aleatorio = random.uniform(85, 100)
            print_log(f"Pausando o envio em {tempo_aleatorio:.2f} segundos", nome_servico)
            time.sleep(tempo_aleatorio)

        except Exception as e:
            print_log(f'Erro: {str(e)}', nome_servico)
            try:
                parametros.MYSQL_CONNECTION.rollback()
            except:
                pass
            inicializa_conexao_mysql()
            time.sleep(5)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    iniciar_envio()
